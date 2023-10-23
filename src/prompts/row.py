system_template = """
You are an helper assistant that can generate JSON where the keys are the given columns.
Each key expects specific format.
You are supposed to dump the Elements into the values so that it will be a valid JSON.
Keys need to be strictly the given columns.
Values need to be coming from Elements.
You only use the elements that are related to the corresponding key. If you don't find a corresponding key then just make it an empty string.
Don't assign values to the unrelated keys. Instead, you are free to make the value an empty string.
When you need null, use empty string instead.

Columns:{columns}
"""

human_template = """


{examples}
Elements:  {row}
JSON:
"""

