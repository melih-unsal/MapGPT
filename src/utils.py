import pandas as pd
import random
import json
import functools
import operator


def getColumnGroups(df):
    identical_columns = {}
    # Compare all pairs of columns
    for col1 in df.columns:
        for col2 in df.columns:
            # Skip if the same column or if col2 is already in the dictionary
            if col1 == col2 or col2 in identical_columns:
                continue

            # Check if the columns have the same content
            if df[col1].equals(df[col2]):
                # If col1 is already in the dictionary, add col2 to the list of its identical columns
                if col1 in identical_columns:
                    identical_columns[col1].append(col2)
                # Otherwise, initialize a new list with col1 and col2
                else:
                    identical_columns[col1] = [col1, col2]
    
    found_columns = set()
    for cols in identical_columns.values():
        found_columns |= set(cols)
    remaining_columns = set(df.columns) - found_columns
    all_columns = remaining_columns | set(identical_columns.keys())
    all_columns = list(all_columns)
    return df.loc[:,all_columns], identical_columns 

def prepareDFForCell(table, index=-1,count=None, another_table_json=None):
    table = getTable(table, index, count)
    # Check if the input is a pandas DataFrame
    if not isinstance(table, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    json_str = ""
    
    if another_table_json is not None:
        another_table = dict2row(another_table_json)
        no_empty_str_cols = another_table.columns[~another_table.apply(lambda col: col.astype(str).eq('').any())]
        table = table[no_empty_str_cols]
        
    for row in table.itertuples(index=False):
        # Convert the row to a dictionary
        row_dict = row._asdict()
        
        json_str += json.dumps(row_dict) + "\n"
    
    return json_str.strip()  # Remove the trailing newline if present

def getTargetCols(mapping):
    return functools.reduce(operator.or_, (set(val) for val in mapping.values()))

def getMappingFromRowResult(res, df1, df2):
    """df1 and df2 are both dataframes
    """
    
    mappings = {}
    
    columns1 = {}
    columns2 = {}
    for col, cell in df1.iloc[0].items():
        col = str(col)
        cell = str(cell)
        cols = columns1.get(cell,[])
        cols.append(col)
        columns1[cell] = cols
    for col, cell in df2.iloc[0].items():
        col = str(col)
        cell = str(cell)
        cols = columns2.get(cell,[])
        cols.append(col)
        columns2[cell] = cols
    for cell1, cells2 in res.items():
        cell1 = str(cell1)
        cols1 = columns1.get(cell1,[])
        cols2 = []
        for cell in cells2:
            cell = str(cell)
            cols2.extend(columns2.get(cell,[]))
        for col1 in cols1:
            for col2 in cols2:
                col1 = str(col1)
                col2 = str(col2)
                mappings[col1] = mappings.get(col1,[]) + [col2]
    for k,v in mappings.items():
        mappings[k] = list(set(v))
    return mappings
            
        
        
    
def getTableArray(df):
    no_empty_str_cols = df.columns[~df.apply(lambda col: col.astype(str).eq('').any())]
    df = df[no_empty_str_cols] 
    return df.iloc[0].values

def getTableString(df):
    no_empty_str_cols = df.columns[~df.apply(lambda col: col.astype(str).eq('').any())]
    df = df[no_empty_str_cols]
    return df.to_json(orient='records', lines=True)

def getTable(df, index=-1,count=None):
    if count is None:
        return df
    return df.iloc[index:index+count,:]

def dict2row(dict):
    new_dict = {}
    for k,v in dict.items():
        if isinstance(v,list):
            new_dict[k] = v
        else:
            new_dict[k] = [v]
            
    return pd.DataFrame.from_dict(new_dict)
    
def getColumns(df):
    return df.columns

def getRowDF(table, index):
    return table.iloc[index:index+1]
    
def getRow(table, index):
    row = table.iloc[index].to_list()
    return ' '.join([str(item) for item in row])

def getRandomIndices(n, percentage=0.8):
    indices = list(range(n))
    count = int(n*percentage)
    taken_indices = random.sample(indices,count)
    return taken_indices

def getExample(row, columns, percentage=0.8):
    indices = getRandomIndices(len(columns), percentage)
    row = row.tolist()
    new_row = [str(row[i]) for i in indices]
    new_columns = [columns[i] for i in indices]
    """remaining_indices = set(range(len(columns))) - set(indices)
    for index in remaining_indices:
        col = columns[index]
        new_row.append("")
        new_columns.append(col)"""
    json_row = {column:item for item,column in zip(new_row, new_columns)}
    return f"""
Elements:  {' '.join(new_row)}
JSON:{json_row}
    """
    
def getExample_v2(row, columns, percentage=0.8):
    row = [str(item) for item in row.tolist()]
    """remaining_indices = set(range(len(columns))) - set(indices)
    for index in remaining_indices:
        col = columns[index]
        new_row.append("")
        new_columns.append(col)"""
    json_row = {column:item for item,column in zip(row, columns)}
    return f"""
Elements:  {' '.join(row)}
JSON:{json_row}
    """

def getExamples(table, count=3, percentage=0.8):
    examples = ""
    count = min(table.shape[0], count)
    columns = table.columns.to_list()
    for i in range(count):
        print(i)
        example = getExample(table.iloc[i],columns, percentage)
        examples += example+"\n"
    return examples, columns


def getIntermediate(source_path, columns, new_columns):
    # Assuming getTable is defined elsewhere and returns a DataFrame
    df = getTable(source_path).loc[:, columns]

    # Check if new_columns is larger than columns
    if len(new_columns) > len(columns):
        # Calculate how many new columns need to be added
        extra_cols = len(new_columns) - len(columns)
        
        # Add the new empty columns to the DataFrame. These will be filled with empty strings.
        for _ in range(extra_cols):
            df[len(df.columns)] = ""  # Adding a new column with empty strings as values

    # Set the column names to new_columns
    df.columns = new_columns

    return df
        
    