from google.adk.apps import App

from aidefense_google_adk import defend

plugin = defend(mode="enforce")
app = App(name="my_app", root_agent=agent, plugins=[plugin])