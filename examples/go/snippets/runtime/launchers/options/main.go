// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Package main configures the A2A request handler and the OpenTelemetry
// providers that the launcher builds.
package main

import (
	"context"
	"log"
	"log/slog"
	"os"
	"time"

	"github.com/a2aproject/a2a-go/v2/a2asrv"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"
	"google.golang.org/genai"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/llmagent"
	"google.golang.org/adk/v2/cmd/launcher"
	"google.golang.org/adk/v2/cmd/launcher/prod"
	"google.golang.org/adk/v2/model/gemini"
	"google.golang.org/adk/v2/telemetry"
)

func main() {
	ctx := context.Background()

	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
		APIKey: os.Getenv("GOOGLE_API_KEY"),
	})
	if err != nil {
		log.Fatalf("Failed to create model: %v", err)
	}

	a, err := llmagent.New(llmagent.Config{
		Name:        "assistant",
		Model:       model,
		Description: "A helpful assistant.",
		Instruction: "Answer the user's questions.",
	})
	if err != nil {
		log.Fatalf("Failed to create agent: %v", err)
	}

	// Sends spans to the OTLP endpoint in OTEL_EXPORTER_OTLP_TRACES_ENDPOINT.
	exporter, err := otlptracehttp.New(ctx)
	if err != nil {
		log.Fatalf("Failed to create the trace exporter: %v", err)
	}

	config := &launcher.Config{
		AgentLoader: agent.NewSingleLoader(a),
		// --8<-- [start:a2a_options]
		// Passed to a2asrv.NewHandler when the a2a sublauncher is active.
		A2AOptions: []a2asrv.RequestHandlerOption{
			a2asrv.WithLogger(slog.Default()),
			a2asrv.WithAgentInactivityTimeout(5 * time.Minute),
		},
		// --8<-- [end:a2a_options]
		// --8<-- [start:telemetry_options]
		// Used when the launcher builds the OpenTelemetry providers.
		TelemetryOptions: []telemetry.Option{
			telemetry.WithSpanProcessors(sdktrace.NewBatchSpanProcessor(exporter)),
		},
		// --8<-- [end:telemetry_options]
	}

	l := prod.NewLauncher()
	if err := l.Execute(ctx, config, os.Args[1:]); err != nil {
		log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
	}
}
