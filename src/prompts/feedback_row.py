system_template = """
You are a helpful assistant that gets the JSON result of Row Model and human's feedback into it.
Row Model reformatted the given JSON into another JSON with the given keys.
After the user got the result, he gave a feedback to it.
Please refine the Row Model's JSON result according to the human's feedback.
As Row Model, your output should be strictly a JSON.
It is so important to obey the given User Feedback
Only show the non-empty key value pairs
"""

human_template = """
Input JSON:
{source_json}

Row Model's Result:
{result_json}

Found Relations:
{relations}

Keys:{columns}

User Feedback on the Relations:{feedback}

Refined JSON:
"""