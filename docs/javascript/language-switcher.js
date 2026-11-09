/*
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
 * Header SDK switcher for the language-scoped docs (/python/, /go/, ...).
 *
 * The language list is read from the switcher's <option>s, which the theme
 * renders from langscope/config.py. Exposes window.adkLanguage for the
 * search scoping script in overrides/main.html.
 */
(function () {
  var STORAGE_KEY = "adk-lang";

  function select() {
    return document.getElementById("adk-lang-select");
  }

  function keys() {
    var s = select();
    return s ? Array.prototype.map.call(s.options, function (o) { return o.value; }) : [];
  }

  function defaultLang() {
    var box = document.querySelector("[data-adk-lang-switcher]");
    return (box && box.getAttribute("data-default")) || keys()[0] || null;
  }

  // The site root path, so a deploy under a subpath still finds the scope.
  function root() {
    return window.__md_scope ? window.__md_scope.pathname : "/";
  }

  function relativePath() {
    var path = window.location.pathname;
    var base = root();
    return path.indexOf(base) === 0 ? path.slice(base.length) : path.replace(/^\//, "");
  }

  function current() {
    var seg = relativePath().split("/")[0];
    return keys().indexOf(seg) >= 0 ? seg : null;
  }

  function saved() {
    try {
      var value = localStorage.getItem(STORAGE_KEY);
      return keys().indexOf(value) >= 0 ? value : null;
    } catch (e) {
      return null;
    }
  }

  function save(value) {
    try { localStorage.setItem(STORAGE_KEY, value); } catch (e) {}
  }

  // The SDK search and navigation should use: the page's own, else the
  // reader's saved choice, else the default.
  function preferred() {
    return current() || saved() || defaultLang();
  }

  function onChange(event) {
    var target = event.target.value;
    save(target);
    var cur = current();
    var fallback = root() + target + "/get-started/";
    if (!cur) {
      window.location.href = fallback;
      return;
    }
    var candidate = root() + target + "/" + relativePath().slice(cur.length + 1);
    fetch(candidate, { method: "HEAD" })
      .then(function (r) {
        window.location.href = r.ok ? candidate + window.location.hash : fallback;
      })
      .catch(function () {
        window.location.href = fallback;
      });
  }

  // Runs on first load and after every instant-navigation page swap: the
  // header (and so the select) survives the swap and must be resynced.
  function sync() {
    var s = select();
    if (!s) return;
    var cur = current();
    // Remember the first SDK a reader lands in. After that only an explicit
    // choice changes it, so following a cross-SDK link (say, to a Python-only
    // page from the Go docs) does not silently switch their preference.
    if (cur && !saved()) save(cur);
    s.value = preferred();
    if (!s.dataset.adkWired) {
      s.dataset.adkWired = "1";
      s.addEventListener("change", onChange);
    }
  }

  window.adkLanguage = { keys: keys, current: current, preferred: preferred };

  if (window.document$) {
    window.document$.subscribe(sync);
  } else {
    document.addEventListener("DOMContentLoaded", sync);
  }
})();
