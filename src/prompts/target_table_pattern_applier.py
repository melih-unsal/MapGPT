system_template = """
You are an assistant that can transform the given JSON by considering the Patterns without changing the keys.
By considering those style patterns, change the values of the JSON

Patterns:

{patterns}
"""

human_template = """
JSON: {json}

Transformed JSON:
"""