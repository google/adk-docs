from google.adk import Agent
from pydantic import BaseModel

class FlightSearchInput(BaseModel):
    origin: str           # Airport code "SFO"
    destination: str      # Airport code "CDG"
    departure_date: date  # date(2026, 3, 15)
    passengers: int = 1   # Number of passengers

class FlightSearchOutput(BaseModel):
    flights: list[Flight]
    cheapest_price: float

flight_searcher = Agent(
    name="flight_searcher",
    instruction="Search for available flights.",
    input_schema=FlightSearchInput,
    output_schema=FlightSearchOutput,
    tools=[search_flights_api],
    mode="single_turn",
    ...
)

assistant = Agent(
    name="assistant",
    instruction="You help users plan trips.",
    sub_agents=[flight_searcher],
    ...
)