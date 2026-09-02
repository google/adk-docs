import langwatch
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langwatch.setup(
    instrumentors=[GoogleADKInstrumentor()]
)