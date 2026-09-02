class CityTime(BaseModel):
    time_info: str  # time information
    city: str       # city name

def lookup_time_function(city: str):
    """Simulate returning the current time in the specified city."""
    return Event(output=CityTime(time_info='10:10 AM', city=city))

city_report_agent = Agent(
    name="city_report_agent",
    model="gemini-flash-latest",
    input_schema=CityTime,

    # data selection based on class and parameter
    # instruction="""
    #     Return a sentence in the following format:
    #     It is {CityTime.time_info} in {CityTime.city} right now.
    # """,

    # more restrictive data selection based on source node name
    instruction="""
        Return a sentence in the following format:
        It is <CityTime.time_info from lookup_time_function> in
        <CityTime.city from lookup_time_function> right now.
    """,
)

root_agent = Workflow(
    name="root_agent",
    edges=[
        (START, city_generator_agent, lookup_time_function, city_report_agent)
    ],
)