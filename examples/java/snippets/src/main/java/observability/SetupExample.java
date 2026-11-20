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

package observability;

// --8<-- [start:full_example]

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.apps.App;
import com.google.adk.plugins.LoggingPlugin;
import com.google.adk.runner.Runner;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.exporter.otlp.trace.OtlpGrpcSpanExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;

/** A basic example demonstrating how to set up observability in ADK Java. */
public class SetupExample {

  public static void main(String[] args) {
    // 1. Configure OpenTelemetry (Traces)
    // ADK Java uses GlobalOpenTelemetry to resolve its tracer.
    // Register the global OpenTelemetry SDK before starting the agent.
    OtlpGrpcSpanExporter spanExporter =
        OtlpGrpcSpanExporter.builder().setEndpoint("http://localhost:4317").build();

    Resource resource =
        Resource.getDefault()
            .merge(
                Resource.create(
                    Attributes.of(AttributeKey.stringKey("service.name"), "my-java-agent")));

    SdkTracerProvider tracerProvider =
        SdkTracerProvider.builder()
            .addSpanProcessor(BatchSpanProcessor.builder(spanExporter).build())
            .setResource(resource)
            .build();

    OpenTelemetrySdk openTelemetry =
        OpenTelemetrySdk.builder().setTracerProvider(tracerProvider).buildAndRegisterGlobal();

    // 2. Optional: Configure ADK Telemetry behavior
    // To capture full message content in traces (defaults to false; use with caution in
    // production), set the ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS=true environment variable
    // before running the application.

    // 3. Initialize Agent and Runner with LoggingPlugin for console output
    LlmAgent agent =
        LlmAgent.builder().name("my_agent").model("gemini-flash-latest").build();

    App app =
        App.builder()
            .name("my_agent")
            .rootAgent(agent)
            .plugins(new LoggingPlugin())
            .build();

    Runner runner = Runner.builder().app(app).build();

    // The runner will now automatically emit traces via GlobalOpenTelemetry
    // and log activity to the console via the LoggingPlugin.
    RunConfig runConfig = RunConfig.builder().autoCreateSession(true).build();
    runner
        .runAsync("user123", "session456", Content.fromParts(Part.fromText("Hello!")), runConfig)
        .blockingSubscribe();

    openTelemetry.close();
  }
}
// --8<-- [end:full_example]
