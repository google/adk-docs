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
	Status            string `json:"status"`
	UpdatedPreference string `json:"updated_preference"`
}

func updateUserPreference(ctx tool.Context, args updateUserPreferenceArgs) updateUserPreferenceResult {
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
		return updateUserPreferenceResult{Status: "error"}
	}

	fmt.Printf("Tool: Updated user preference '%s' to '%s'\n", args.Preference, args.Value)
	return updateUserPreferenceResult{Status: "success", UpdatedPreference: args.Preference}
}

// --8<-- [end:example]
