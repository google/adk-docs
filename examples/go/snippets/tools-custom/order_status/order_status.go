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
