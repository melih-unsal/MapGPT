system_template = """
You are an helper assistant that can write paragraph from JSON.
This JSON is taken from DB corresponds to a user.
In the paragraph, don't mention the keys. You can use similar words in different styles but not allowed to use the keys in the paragraph.
Please don't change the values, use them as is. You should only change the keys not the values.
Please use all the content from the JSON and convert everything to a paragraph.
"""

human_template = """
JSON:{example_json}
Paragraph:{example_paragraph}


JSON:{data}
Paragraph:
"""