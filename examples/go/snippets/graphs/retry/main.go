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

// Package main demonstrates per-node retry and timeout configuration in ADK Go
// v2 graph workflows, using workflow.NodeConfig, workflow.RetryConfig, and
// workflow.DefaultRetryConfig.
//
// NOTE: This file requires google.golang.org/adk/v2 (the workflow package),
// available in ADK Go v2.0.0 and higher.
//
// This file contains one snippet region used in docs/graphs/retry.md:
//
//	get-started – a flaky node with a retry policy and a per-attempt timeout
package main

import (
	"context"
	"errors"
	"log"
	"math/rand"
	"time"

	"google.golang.org/adk/v2/agent"
	"google.golang.org/adk/v2/agent/workflowagent"
	"google.golang.org/adk/v2/workflow"
)

// --8<-- [start:get-started]
// errServiceUnavailable stands in for a transient failure from a remote service.
var errServiceUnavailable = errors.New("forecast service unavailable")

func newForecastWorkflow() (agent.Agent, error) {
	// fetchForecast simulates a slow, unreliable service call. It watches
	// ctx.Done() so that the node's timeout can stop it.
	fetchForecast := func(ctx agent.Context, _ any) (string, error) {
		select {
		case <-time.After(200 * time.Millisecond):
		case <-ctx.Done():
			return "", ctx.Err()
		}
		if rand.Float64() < 0.5 {
			return "", errServiceUnavailable
		}
		return "sunny", nil
	}

	// Start from the default policy and override only what you need.
	retry := workflow.DefaultRetryConfig()
	retry.MaxAttempts = 3 // 1 original attempt + 2 retries
	retry.InitialDelay = time.Second
	// Retry only transient failures: the service error and the node's own
	// timeout, which surfaces as context.DeadlineExceeded.
	retry.ShouldRetry = func(err error) bool {
		return errors.Is(err, errServiceUnavailable) ||
			errors.Is(err, context.DeadlineExceeded)
	}

	fetchNode := workflow.NewFunctionNode("fetch_forecast", fetchForecast,
		workflow.NodeConfig{
			RetryConfig: retry,
			Timeout:     10 * time.Second, // limit for each attempt
		},
	)

	reportNode := workflow.NewFunctionNode("report_forecast",
		func(_ agent.Context, forecast string) (string, error) {
			return "The forecast is " + forecast + ".", nil
		},
		workflow.NodeConfig{},
	)

	return workflowagent.New(workflowagent.Config{
		Name:  "forecast_workflow",
		Edges: workflow.Chain(workflow.Start, fetchNode, reportNode),
	})
}

// --8<-- [end:get-started]

func main() {
	forecastAgent, err := newForecastWorkflow()
	if err != nil {
		log.Fatalf("newForecastWorkflow: %v", err)
	}
	log.Printf("created %s", forecastAgent.Name())
}
