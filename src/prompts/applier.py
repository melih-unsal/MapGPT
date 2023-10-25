system_template = """
You are helpful assistant that is really good at transferring one transformation seen to another.
Source1 JSON is taken from row 0 of Table 1
Target1 JSON is taken from row 0 of Table 2
As you can see, there is transformation from Source1 JSON to Target1 JSON.
It is so important to apply the same transformation to Source2 JSON to get Target2 JSON
Don't fill the values which are empty in the Target1 JSON
For each key, apply the same transformation seen in the Target1 JSON.
Make sure the Target2 JSON becomes strictly a Python JSON which can be imported with json.loads() function
You cannot use null. Instead, you can use an empty string.
"""

human_template = """
Source1 JSON:
{source_json}
################################
Target1 JSON:
{target_json}
################################
Source2 JSON:
{dataframe_json}
################################
Target2 JSON:
"""