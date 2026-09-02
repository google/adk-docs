plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID") # Optional: omit to use all connected accounts
for tool in plugin.get_tools():
    print(f"{tool.name}: {tool.description}")