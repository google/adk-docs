from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset

connector_tool = ApplicationIntegrationToolset(
    project="test-project", # TODO: replace with GCP project of the connection
    location="us-central1", #TODO: replace with location of the connection
    connection="test-connection", #TODO: replace with connection name
    entity_operations={"Entity_One": ["LIST","CREATE"], "Entity_Two": []},#empty list for actions means all operations on the entity are supported.
    actions=["action1"], #TODO: replace with actions
    service_account_json='{...}', # optional. Stringified json for service account key
    tool_name_prefix="tool_prefix2",
    tool_instructions="..."
)