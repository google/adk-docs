from aidefense_google_adk import make_agentsec_callbacks

cbs = make_agentsec_callbacks(mode="enforce", fail_open=True)
cbs.apply_to(agent)