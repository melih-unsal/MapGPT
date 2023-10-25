system_template = """
You are an helper assistant that can refine the given Result JSON by looking at the Source Elements and Example JSON.
In the Result JSON, some values might be hallucinated or could be inferred from the Source Elements.
To make sure that you don't miss anything, investigate the Example JSON.
Only use values from Elements. Use Example JSON only for style and formats
The Refined JSON will have the same keys of Result JSON
Refined JSON will be strictly as Python JSON.
You cannot use null. Instead, you can use an empty string.
"""

human_template = """
Example JSON:{target_json}

Result JSON:{source_json}

Elements:{array}

Refined JSON:
"""