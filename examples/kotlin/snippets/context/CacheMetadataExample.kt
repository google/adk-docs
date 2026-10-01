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

package com.google.adk.kt.examples.context

import com.google.adk.kt.events.Event

// --8<-- [start:cache_metadata]

/** Reports whether the context cache was used for the LLM call behind [event]. */
fun logCacheUse(event: Event) {
    // Null when caching is disabled, and on any event whose LLM call produced
    // no cache information.
    val cache = event.cacheMetadata ?: return

    if (!cache.isActive) {
        // Fingerprint-only: ADK measured the cacheable prefix but no cache is in
        // use. That is the first turn, a prefix that changed since the last turn,
        // or a cache ADK did not create -- most often because the cacheable
        // prefix was below minTokens.
        println("Not cached yet; fingerprinted ${cache.contentsCount} contents.")
        return
    }

    println("Cache ${cache.cacheName} reused ${cache.invocationsUsed} time(s).")
    if (cache.expireSoon) {
        // Advisory only. ADK goes on reusing the cache until it actually expires,
        // so this is a heads-up for your own code, not a prediction about the
        // next turn.
        println("Cache is at or near expiry.")
    }
}
// --8<-- [end:cache_metadata]
