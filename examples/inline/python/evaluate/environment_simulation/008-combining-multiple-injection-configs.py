ToolSimulationConfig(
    tool_name="get_inventory",
    injection_configs=[
        # Always fail for a specific out-of-stock item
        InjectionConfig(
            match_args={"sku": "OOS-001"},
            injected_response={"quantity": 0, "available": False},
        ),
        # Randomly fail 20% of the time for all other items
        InjectionConfig(
            injection_probability=0.2,
            random_seed=7,
            injected_error=InjectedError(
                injected_http_error_code=503,
                error_message="Inventory service unavailable.",
            ),
        ),
    ],
)