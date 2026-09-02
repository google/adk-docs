async def initial_prompt(ctx: Context):
   """Ask the user for itinerary information"""
   input_message = """
       This is an interactive concierge workflow tasked with making you a great
       itinerary for you in your city of choice. If you give some details about
       yourself or what you are generally looking for I can better personalize
       your itinerary.
       For example, input your:
           City (Required),
           Age,
           Hobby,
           Example of attraction you liked
   """
   yield RequestInput(message=input_message, response_schema=str)