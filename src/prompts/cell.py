system_template = """
You are an helper assistant that can reformat the given Source JSON values
By looking at the Style Reference, please reformat Source JSON values in a way that for each value in the key,value pair, it seems compatible with the the values in Style Reference
Make sure that the whole content and information is coming from the Source JSON and only style is coming from the Style Reference.
Keep in mind that style means the format of date, id and any common pattern throughout the Style Reference. Be careful on those patterns while reformatting.

Non-empty Keys:{columns}
"""

human_template = """
Style Reference:
{table2}

Source JSON:
{table1}

Refined JSON:
"""

