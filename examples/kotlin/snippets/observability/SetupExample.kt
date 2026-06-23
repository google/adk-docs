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

package com.google.adk.kt.examples.observability

import com.google.adk.kt.agents.LlmAgent
import com.google.adk.kt.models.Gemini
import com.google.adk.kt.plugins.LoggingPlugin
import com.google.adk.kt.plugins.PluginManager
import com.google.adk.kt.runners.InMemoryRunner
import com.google.adk.kt.telemetry.TelemetryConfig
import com.google.adk.kt.types.Content
import com.google.adk.kt.types.Role
import io.opentelemetry.api.common.AttributeKey
import io.opentelemetry.api.common.Attributes
import io.opentelemetry.exporter.otlp.trace.OtlpGrpcSpanExporter
import io.opentelemetry.sdk.OpenTelemetrySdk
import io.opentelemetry.sdk.resources.Resource
import io.opentelemetry.sdk.trace.SdkTracerProvider
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor

/** A basic example demonstrating how to set up observability in ADK Kotlin. */
suspend fun main() {
    // --8<-- [start:full_example]
    // 1. Configure OpenTelemetry (Traces)
    // ADK Kotlin uses GlobalOpenTelemetry to resolve its tracer on the JVM.
    val spanExporter = OtlpGrpcSpanExporter.builder().setEndpoint("http://localhost:4317").build()

    val resource =
        Resource.getDefault()
            .merge(
                Resource.create(
                    Attributes.of(AttributeKey.stringKey("service.name"), "my-kotlin-agent"),
                ),
            )

    val tracerProvider =
        SdkTracerProvider.builder()
            .addSpanProcessor(BatchSpanProcessor.builder(spanExporter).build())
            .setResource(resource)
            .build()

    OpenTelemetrySdk.builder().setTracerProvider(tracerProvider).buildAndRegisterGlobal()

    // 2. Optional: Configure ADK Telemetry behavior
    // Enable capturing full message content in traces (use with caution in production)
    TelemetryConfig.captureMessageContent = true

    // 3. Initialize Agent and Runner with LoggingPlugin for console output
    val agent = LlmAgent(name = "my_agent", model = Gemini(name = "gemini-flash-latest"))

    val runner =
        InMemoryRunner(agent = agent, pluginManager = PluginManager(listOf(LoggingPlugin())))

    // The runner will now automatically emit traces via GlobalOpenTelemetry
    // and log activity to the console via the LoggingPlugin.
    runner.run(
        userId = "user123",
        sessionId = "session456",
        newMessage = Content.fromText(Role.USER, "Hello!"),
    )
    // --8<-- [end:full_example]
}
