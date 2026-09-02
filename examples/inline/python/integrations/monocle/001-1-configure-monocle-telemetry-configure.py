from monocle_apptrace import setup_monocle_telemetry

# Initialize Monocle telemetry - automatically instruments Google ADK
setup_monocle_telemetry(workflow_name="my-adk-app")