system_template = """
You are a helpful assistant that can get the common patterns of keys in the DATA. For each key generate at most 1 pattern

Key : key_name
Pattern: pattern
"""

human_template = """
DATA:

{examples}

Based on given DATA, identify the patterns and generate a response in the specified format.
"""