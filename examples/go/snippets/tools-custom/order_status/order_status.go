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

// --8<-- [start:snippet]
import (
	"fmt"

	"google.golang.org/adk/tool"
)

type lookupOrderStatusArgs struct {
	OrderID string `json:"order_id" jsonschema:"The ID of the order to look up."`
}

type order struct {
	State          string `json:"state"`
	TrackingNumber string `json:"tracking_number"`
}

type lookupOrderStatusResult struct {
	Status       string `json:"status"`
	Order        order  `json:"order,omitempty"`
	ErrorMessage string `json:"error_message,omitempty"`
}

func lookupOrderStatus(ctx tool.Context, args lookupOrderStatusArgs) lookupOrderStatusResult {
	// ... function implementation to fetch status ...
	if statusDetails, ok := fetchStatusFromBackend(args.OrderID); ok {
		return lookupOrderStatusResult{
			Status: "success",
			Order: order{
				State:          statusDetails.State,
				TrackingNumber: statusDetails.Tracking,
			},
		}
	}
	return lookupOrderStatusResult{Status: "error", ErrorMessage: fmt.Sprintf("Order ID %s not found.", args.OrderID)}
}

// --8<-- [end:snippet]

type statusDetails struct {
	State    string
	Tracking string
}

func fetchStatusFromBackend(orderID string) (statusDetails, bool) {
	if orderID == "12345" {
		return statusDetails{State: "shipped", Tracking: "1Z9..."}, true
	}
	return statusDetails{}, false
}
