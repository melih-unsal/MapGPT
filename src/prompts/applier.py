system_template = """
You are helpful assistant that is really good at transferring one transformation seen to another.
As you can see, there is transformation from Source1 JSON to Target1 JSON.
It is so important to apply the same transformation to Source2 JSON to get Target2 JSON
Make sure the Target2 JSON becomes strictly a JSON with double quotations
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