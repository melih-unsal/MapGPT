system_template = """
You are an helper assistant that can reformat the given Broken JSON where there might be problems inside of its values.
Its keys are perfect but values might have a style problem
By looking at the Reference JSONs, please reformat its values in a way that for each value in the key,value pair, it seems compatible with the Reference JSONs
Refined JSON will be strictly a Python JSON
You cannot use null. Instead, you can use an empty string.
Non-empty Keys:{columns}
"""

human_template = """
Reference JSONs:
{table2}

Broken JSON:
{table1}

Refined JSON:
"""

