system_template = """
You are an helper assistant that can reformat the given Broken JSON where there might be problems inside of its values not keys.
Its keys are perfect but values might have a style problem
By looking at the Reference JSONs, please reformat it in a way that for each key, it seems compatible with the Reference JSONs

Non-empty Keys:{columns}
"""

human_template = """
Reference JSONs:
{table2}

Broken JSON:
{table1}

Refined JSON:
"""

