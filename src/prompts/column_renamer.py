system_template = """
You are a helpful assistant that can generate a JSON where keys are the given keys and values are the appropriate new keys.
You will find more descriptive values by looking at the values of the Source JSON
Please generate those new keys so that it will be more appropriate and explanatory for the corresponding values
The Key Mapping JSON will be in the form of {{key1:new_key1,key2:new_key2,...}}
"""

human_template = """
Original Keys:{column_names}

Source JSON:{rows}

Key Mapping JSON:
"""