from dbos_google_adk import DBOSEventSummarizer
from google.adk.models.google_llm import Gemini

summarizer = DBOSEventSummarizer.from_llm(Gemini(model="gemini-flash-latest"))