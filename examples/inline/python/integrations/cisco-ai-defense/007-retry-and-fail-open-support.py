from google.adk.apps import App

from aidefense_google_adk import AgentsecPlugin

app = App(
    name="my_app",
    root_agent=agent,
    plugins=[
        AgentsecPlugin(
            mode="enforce",
            fail_open=True,
            retry_total=3,
            retry_backoff=0.5,
        ),
    ],
)