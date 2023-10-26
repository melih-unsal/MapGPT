system_template = """
You are helpful assistant that can convert the table into Python JSON so that it can be convertable to dataframe using pd.DataFrame.from_dict
The column names are as follows: {columns}
You cannot use null. Instead, you can use an empty string.
"""

human_template = """
Table:{table}
JSON:
"""

