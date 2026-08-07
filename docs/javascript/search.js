/**
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*
 * Search modal backed by Pagefind.
 *
 * Nothing search-related is fetched on page load. `pagefind.js` (12.8 KB
 * gzipped) is dynamically imported when the modal is first opened, and
 * `pagefind-highlight.js` (9.6 KB gzipped) only when the current URL carries
 * highlight terms, which happens only when arriving from a search result.
 */
(() => {
  "use strict";

  /*
   * Belt and braces, not a live guard.
   *
   * Material's instant navigation re-evaluates only the scripts it finds
   * inside the container it swaps -- roughly `Ke(M("script", Ce("container")))`
   * in the bundled runtime. extra_javascript is emitted outside that
   * container, so this file is never re-evaluated and the flag can never
   * actually be observed as true. It stays because it is free and because
   * the failure it prevents is silent.
   *
   * If the trigger or dialog is ever moved into a replaced region, this
   * guard becomes the bug rather than the fix: the script would keep the
   * references it captured below, they would point at detached nodes after
   * the first client-side navigation, and search would stop working with no
   * error. Re-check this if either element moves.
   */
  if (window.__adkSearchInitialised) return;

  const dialog = document.querySelector("[data-adk-search-dialog]");
  const trigger = document.querySelector("[data-adk-search-trigger]");
  if (!dialog || !trigger) return;

  window.__adkSearchInitialised = true;

  const input = dialog.querySelector("[data-adk-search-input]");
  const results = dialog.querySelector("[data-adk-search-results]");
  const status = dialog.querySelector("[data-adk-search-status]");
  const closeButton = dialog.querySelector("[data-adk-search-close]");

  const MAX_PAGES = 5;
  const MAX_SECTIONS = 3;
  const DEBOUNCE_MS = 300;
  const HIGHLIGHT_PARAM = "pagefind-highlight";
  const ACTIVE_CLASS = "adk-search__link--active";
  const OPTION_ID_PREFIX = "adk-search-option-";

  /*
   * Resolved now, at initial page load. The header survives instant
   * navigation, so the rendered relative path would resolve against the
   * wrong document if this were deferred until the modal opens.
   */
  const BUNDLE = new URL(dialog.dataset.pagefindBundle, document.baseURI).href;

  let cursor = -1;

  /*
   * Memoised so the warm-up fired by openDialog() and the first keystroke
   * share one load instead of racing. Pagefind's own init_pagefind() happens
   * to be idempotent, but that is an undocumented internal detail and not
   * something to depend on.
   *
   * The module is only published to callers once options() and init() have
   * both succeeded. Resolving to the raw module earlier would mean a failed
   * init still handed back a truthy, unusable engine -- the likeliest
   * failure mode in production (CSP blocking wasm, a partial deploy, a
   * corrupt entry file) is exactly the one that must reach the error UI.
   */
  let pagefindPromise = null;

  function loadPagefind() {
    pagefindPromise ??= (async () => {
      const mod = await import(`${BUNDLE}pagefind.js`);
      await mod.options({
        excerptLength: 20,
        // Makes Pagefind append the term to every result URL itself.
        highlightParam: HIGHLIGHT_PARAM,
      });
      await mod.init();
      return mod;
    })().catch((error) => {
      console.error("Pagefind failed to load", error);
      return null;
    });
    return pagefindPromise;
  }

  function setStatus(message) {
    status.textContent = message;
  }

  function renderExcerpt(html) {
    const paragraph = document.createElement("p");
    paragraph.className = "adk-search__excerpt";
    /*
     * Safe against injection: pagefind.js escapes `<` and `>` in
     * `fragment.raw_content` before building excerpts (`loadFragment`,
     * pagefind 1.5.2), so the only markup reaching innerHTML is Pagefind's
     * own <mark>. calculate_sub_results reads the same escaped
     * raw_content, so section excerpts are covered by the same guarantee.
     * Re-verify on any Pagefind bump.
     *
     * Note this does not rest on trusting page content. Raw fragments really
     * do contain unescaped `<a href=...>` and things like `Optional<Content>`
     * from the API docs; it is that escape step, not the provenance of the
     * text, that makes this safe.
     */
    paragraph.innerHTML = html || "";
    return paragraph;
  }

  /*
   * Result links opt out of Material's instant navigation via target="_self".
   *
   * Material intercepts internal links by stripping the query and hash and
   * testing the bare URL against its sitemap, so `/page/?pagefind-highlight=x`
   * would be intercepted and handled client-side. That would leave the
   * dialog open over the new page and, because the document is never
   * replaced, the arrival highlighting at the bottom of this file would
   * never run. Material's handler bails out early on a truthy `target`, so
   * setting it forces a full navigation, which both tears down the dialog
   * and re-runs this script.
   *
   * The links are also the listbox options: role, aria-selected and id are
   * what make the arrow-key cursor perceivable to assistive tech. The ids
   * are assigned in runSearch once the full list exists.
   */
  function renderPage(page) {
    const item = document.createElement("li");
    item.className = "adk-search__page";
    // Options are the <a>s; the list plumbing carries no semantics.
    item.setAttribute("role", "presentation");

    const link = document.createElement("a");
    link.className = "adk-search__page-link";
    link.href = page.url;
    link.target = "_self";
    link.setAttribute("role", "option");
    link.setAttribute("aria-selected", "false");
    link.textContent = (page.meta && page.meta.title) || page.url;
    item.appendChild(link);

    const sections = (page.sub_results || [])
      .filter((section) => section.url !== page.url)
      .slice(0, MAX_SECTIONS);

    if (sections.length === 0) {
      item.appendChild(renderExcerpt(page.excerpt));
      return item;
    }

    const list = document.createElement("ul");
    list.className = "adk-search__sections";
    list.setAttribute("role", "presentation");
    for (const section of sections) {
      const sectionItem = document.createElement("li");
      sectionItem.setAttribute("role", "presentation");
      const sectionLink = document.createElement("a");
      sectionLink.className = "adk-search__section-link";
      sectionLink.href = section.url;
      sectionLink.target = "_self";
      sectionLink.setAttribute("role", "option");
      sectionLink.setAttribute("aria-selected", "false");

      const title = document.createElement("span");
      title.className = "adk-search__section-title";
      title.textContent = section.title;

      sectionLink.append(title, renderExcerpt(section.excerpt));
      sectionItem.appendChild(sectionLink);
      list.appendChild(sectionItem);
    }
    item.appendChild(list);
    return item;
  }

  // Clears the rendered list and every piece of state that describes it.
  function clearResults() {
    setCursor(-1);
    results.replaceChildren();
    setExpanded(false);
  }

  async function runSearch(rawQuery) {
    const query = rawQuery.trim();
    /*
     * Reset the cursor against the list that is on screen right now, not the
     * one that will replace it. The rendering below is at least DEBOUNCE_MS
     * away, and until then the previously active row is still displayed;
     * resetting the index alone would leave it looking selected while Enter
     * did nothing.
     */
    setCursor(-1);

    if (!query) {
      clearResults();
      setStatus("");
      return;
    }

    const engine = await loadPagefind();
    if (!engine) {
      clearResults();
      setStatus("Search is unavailable. Try reloading the page.");
      return;
    }

    try {
      const search = await engine.debouncedSearch(query, {}, DEBOUNCE_MS);
      // Resolves to null when a later keystroke superseded this call.
      if (search === null) return;
      // Ignore a response that arrived after the box was cleared or changed.
      if (input.value.trim() !== query) return;

      if (search.results.length === 0) {
        clearResults();
        setStatus(`No results for "${query}"`);
        return;
      }

      const pages = await Promise.all(
        search.results.slice(0, MAX_PAGES).map((result) => result.data())
      );
      if (input.value.trim() !== query) return;

      setCursor(-1);
      results.replaceChildren(...pages.map(renderPage));
      resultLinks().forEach((link, index) => {
        link.id = `${OPTION_ID_PREFIX}${index}`;
      });
      setExpanded(true);
      /*
       * Announced by the role="status" region. Reporting both numbers is the
       * only signal that MAX_PAGES has truncated the list.
       */
      const total = search.results.length;
      setStatus(
        total === pages.length
          ? `${total} result${total === 1 ? "" : "s"}`
          : `${total} results, showing top ${pages.length}`
      );
    } catch (error) {
      /*
       * debouncedSearch() and result.data() both fetch over the network --
       * index chunks and fragment files are pulled per query. Without this
       * the rejection escapes into the input listener, which ignores it: an
       * unhandled rejection, stale results left on screen, and no signal.
       */
      console.error("Pagefind search failed", error);
      clearResults();
      setStatus("Search failed. Check your connection and try again.");
    }
  }

  function resultLinks() {
    return Array.from(results.querySelectorAll("a"));
  }

  function setExpanded(expanded) {
    input.setAttribute("aria-expanded", expanded ? "true" : "false");
  }

  /*
   * The single place the selection is written. It keeps three things in
   * step that used to drift apart: the index, the visual highlight, and the
   * accessible selection. Passing -1 means "nothing selected" and clears the
   * highlight from every link currently rendered, which is what makes a
   * reset safe to do while an older list is still on screen.
   */
  function setCursor(next) {
    const links = resultLinks();
    cursor = next >= 0 && next < links.length ? next : -1;
    links.forEach((link, index) => {
      const active = index === cursor;
      link.classList.toggle(ACTIVE_CLASS, active);
      link.setAttribute("aria-selected", active ? "true" : "false");
    });
    if (cursor >= 0) {
      input.setAttribute("aria-activedescendant", links[cursor].id);
      links[cursor].scrollIntoView({ block: "nearest" });
    } else {
      input.removeAttribute("aria-activedescendant");
    }
  }

  function moveCursor(delta) {
    const links = resultLinks();
    if (links.length === 0) return;
    /*
     * From "nothing selected", down goes to the first item and up to the
     * last. Folding -1 into the modulo instead would send ArrowUp to
     * links.length - 2, the second-to-last item.
     */
    const next =
      cursor < 0
        ? delta > 0
          ? 0
          : links.length - 1
        : (cursor + delta + links.length) % links.length;
    setCursor(next);
  }

  function openDialog() {
    if (dialog.open) return;
    input.value = "";
    clearResults();
    setStatus("");
    dialog.showModal();
    input.focus();
    // Warm the engine while the reader is still typing their first character.
    loadPagefind();
  }

  trigger.addEventListener("click", openDialog);
  closeButton.addEventListener("click", () => dialog.close());
  input.addEventListener("input", (event) => runSearch(event.target.value));

  /*
   * Closing here is not redundant with the full navigation that target="_self"
   * forces. A result pointing at the page the reader is already on differs
   * from the current URL only by hash, so the browser scrolls instead of
   * loading a document: nothing is torn down and the dialog would otherwise
   * stay open over the anchor it just jumped to.
   */
  results.addEventListener("click", (event) => {
    if (event.target.closest("a")) dialog.close();
  });

  /*
   * Clicking the backdrop closes; clicking inside the panel does not.
   *
   * Both ends of the gesture have to be on the backdrop. A click event is
   * dispatched against the nearest common ancestor of mousedown and mouseup,
   * so selecting text in the input and releasing outside the panel targets
   * the dialog itself and would otherwise close it mid drag-select.
   */
  let backdropPressed = false;
  dialog.addEventListener("mousedown", (event) => {
    backdropPressed = event.target === dialog;
  });
  dialog.addEventListener("click", (event) => {
    if (backdropPressed && event.target === dialog) dialog.close();
    backdropPressed = false;
  });

  /*
   * `code` rather than `key` so the shortcut is the physical K position and
   * does not move around on Dvorak or AZERTY. altKey is excluded because
   * Windows sends AltGr as Ctrl+Alt: on layouts where AltGr+K is a printable
   * character, matching on Ctrl alone would swallow it.
   */
  /*
   * `/`, `s` and `f` were bound by Material's own search, which this replaces.
   * Rebinding them keeps existing muscle memory working instead of silently
   * dropping three shortcuts. They are bare keys, so they must not fire while
   * the reader is typing into a field or editing content.
   */
  const TYPING_TAGS = new Set(["INPUT", "TEXTAREA", "SELECT"]);
  const isTyping = (target) =>
    TYPING_TAGS.has(target.tagName) || target.isContentEditable;

  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && !event.altKey && event.code === "KeyK") {
      event.preventDefault();
      if (dialog.open) dialog.close();
      else openDialog();
      return;
    }
    if (dialog.open || event.ctrlKey || event.metaKey || event.altKey) return;
    if (["/", "s", "f"].includes(event.key) && !isTyping(event.target)) {
      event.preventDefault();
      openDialog();
    }
  });

  dialog.addEventListener("keydown", (event) => {
    /*
     * All three keys are scoped to the combobox. aria-activedescendant only
     * has meaning while the input holds focus, so moving the cursor from the
     * close button would shift a pointer nothing is listening to.
     */
    if (event.target !== input) return;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveCursor(1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      moveCursor(-1);
    } else if (event.key === "Enter") {
      const links = resultLinks();
      if (cursor >= 0 && links[cursor]) {
        event.preventDefault();
        links[cursor].click();
      }
    }
  });

  /*
   * Arrival highlighting. Loaded only when the URL carries highlight terms,
   * so a normal page view never pays for it.
   */
  if (new URLSearchParams(window.location.search).has(HIGHLIGHT_PARAM)) {
    import(`${BUNDLE}pagefind-highlight.js`)
      .then(({ default: PagefindHighlight }) => {
        // Constructing it performs the highlighting.
        new PagefindHighlight({
          highlightParam: HIGHLIGHT_PARAM,
          markContext: document.querySelector("article.md-content__inner"),
          /*
           * Not what prevents the yellow: Pagefind's injected rule is
           * `:where(.pagefind-highlight){...}` at specificity 0-0-0, and
           * Material's own `.md-typeset mark` already outranks it, so the
           * marks would be palette-coloured either way.
           *
           * It is set for two narrower reasons: it keeps a stray <style>
           * element out of <head>, and it removes the injected
           * `color: black`, which is the one declaration that would matter
           * if a mark ever landed outside .md-typeset and so escaped
           * Material's rule.
           */
          addStyles: false,
        });
      })
      .catch((error) => console.error("Pagefind highlight failed to load", error));
  }
})();
