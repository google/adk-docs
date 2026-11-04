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

@file:OptIn(ExperimentalWorkflowApi::class)

package com.google.adk.kt.examples.graphs

// --8<-- [start:get-started]
import com.google.adk.kt.annotations.ExperimentalWorkflowApi
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Role
import com.google.adk.kt.workflow.NodeConfig
import com.google.adk.kt.workflow.RetryConfig
import com.google.adk.kt.workflow.Start
import com.google.adk.kt.workflow.Workflow
import com.google.adk.kt.workflow.emit
import com.google.adk.kt.workflow.node
import com.google.adk.kt.workflow.workflow
import kotlin.random.Random
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.Duration.Companion.seconds
import kotlinx.coroutines.delay

/** Stands in for a transient failure from a remote service. */
class ServiceUnavailableException(message: String) : Exception(message)

/** Simulates an unreliable call to a forecast service. */
val fetchForecast =
  node<Any?, String>(
    "fetch_forecast",
    config =
      NodeConfig(
        retryConfig =
          RetryConfig(
            maxAttempts = 3, // 1 original attempt + 2 retries
            initialDelay = 1.seconds,
            // A timed-out attempt is reported as "NodeTimeoutError".
            exceptions = listOf("ServiceUnavailableException", "NodeTimeoutError"),
          ),
        timeout = 10.seconds, // limit for each attempt
      ),
  ) { context, _ ->
    emit(Content.fromText(Role.MODEL, "Fetching forecast, attempt ${context.attemptCount}"))
    delay(200.milliseconds)
    if (Random.nextDouble() < 0.5) throw ServiceUnavailableException("Forecast service unavailable")
    "sunny"
  }

val reportForecast = node<String, String>("report_forecast") { _, forecast -> "The forecast is $forecast." }

fun createForecastWorkflow(): Workflow =
  workflow("forecast_workflow") { chain(Start, fetchForecast, reportForecast) }
// --8<-- [end:get-started]
