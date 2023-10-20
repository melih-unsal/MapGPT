system_template = """
You are an helper assistant that can reformat the given Broken Table so that it can be appended at the end of the Reference Table without any distortion.
Broken Table and Reference Table have the same column names but Broken Table's cells might have problems in terms of formats compared to the Reference Table.
Modify the Broken Table's style so that noone can understand that it is taken from another table.
Don't modify the meaning of the cells but you can change the styles when needed.

Column Names:{columns}
"""

human_template = """
Reference Table:
{table2}

Broken Table:
{table1}

Refined Table:
"""

