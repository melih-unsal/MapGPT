system_template ="""
You are an helper assistant that can generate JSON from paragraph with the given keys
Try to infer from the paragraph deeply
Don't use null. Instead, you can use an empty string.
The result will be imported with json.load()
JSON keys are like in the below:
{columns}
"""

human_template = """
Paragraph:{target_paragraph}
JSON:{target_json}


Paragraph:{source_paragraph}
JSON:
"""