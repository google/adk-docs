// Copyright 2025 Google LLC
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

package main

// --8<-- [start:example]
import (
	"fmt"

	"google.golang.org/adk/tool"
)

type updateUserPreferenceArgs struct {
	Preference string `json:"preference" jsonschema:"The name of the preference to set."`
	Value      string `json:"value" jsonschema:"The value to set for the preference."`
}

type updateUserPreferenceResult struct {
	UpdatedPreference string `json:"updated_preference"`
}

func updateUserPreference(ctx tool.Context, args updateUserPreferenceArgs) (*updateUserPreferenceResult, error) {
	userPrefsKey := "user:preferences"
	val, err := ctx.State().Get(userPrefsKey)
	if err != nil {
		val = make(map[string]any)
	}

	preferencesMap, ok := val.(map[string]any)
	if !ok {
		preferencesMap = make(map[string]any)
	}

	preferencesMap[args.Preference] = args.Value

	if err := ctx.State().Set(userPrefsKey, preferencesMap); err != nil {
		return nil, err
	}

	fmt.Printf("Tool: Updated user preference '%s' to '%s'\n", args.Preference, args.Value)
	return &updateUserPreferenceResult{
		UpdatedPreference: args.Preference,
	}, nil
}

// --8<-- [end:example]
