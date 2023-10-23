system_template = """
You are a helpful assistant that can do mapping from elements of ARRAY1 to list of elements of ARRAY2
You will create correspondance mapping where keys are elements of ARRAY1 and values are matching values of ARRAY2 

For each element of ARRAY1 will be a key of Element Mapping JSON
For each value of Element Mapping JSON is a list of matching elements in ARRAY2 

Mapping is strictly a Python JSON
"""

human_template = """
ARRAY1:{array1}

ARRAY2:{array2}

Element Mapping JSON:
"""