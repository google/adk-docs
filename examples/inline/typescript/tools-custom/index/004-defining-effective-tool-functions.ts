/**
 * Fetches the current status of a customer's order using its ID.
 *
 * Use this tool ONLY when a user explicitly asks for the status of
 * a specific order and provides the order ID. Do not use it for
 * general inquiries.
 *
 * @param params The parameters for the function.
 * @param params.order_id The unique identifier of the order to look up.
 * @returns A dictionary indicating the outcome.
 *          On success, status is 'success' and includes an 'order' dictionary.
 *          On failure, status is 'error' and includes an 'error_message'.
 *          Example success: {'status': 'success', 'order': {'state': 'shipped', 'tracking_number': '1Z9...'}}
 *          Example error: {'status': 'error', 'error_message': 'Order ID not found.'}
 */
async function lookupOrderStatus(params: { order_id: string }): Promise<Record<string, any>> {
  // ... function implementation to fetch status from a backend ...
  const status_details = await fetchStatusFromBackend(params.order_id);
  if (status_details) {
    return {
      "status": "success",
      "order": {
        "state": status_details.state,
        "tracking_number": status_details.tracking,
      },
    };
  } else {
    return { "status": "error", "error_message": `Order ID ${params.order_id} not found.` };
  }
}

// Placeholder for a backend call
async function fetchStatusFromBackend(order_id: string): Promise<{state: string, tracking: string} | null> {
    if (order_id === "12345") {
        return { state: "shipped", tracking: "1Z9..." };
    }
    return null;
}