system_template = """
You are a helpful assistant that gets the JSON result of Model and human's feedback into it.
Model reformatted the given JSON into another JSON with the given keys.
Keys:{columns}
After the user got the result, he gave a feedback on it.
Please refine the Model's JSON result according to the human's feedback.
Your output should be strictly a JSON.
It is so important to obey the given User Feedback
Only show the non-empty key value pairs
"""

human_template = """
Input JSON:
{source_json}

Model's Result:
{result_json}

User Feedback:{feedback}

Refined JSON:
"""