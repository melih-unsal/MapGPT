import pandas as pd
import random
import json
#from tabulate import tabulate

def prepareDFForCell(table, index=-1,count=None):
    table = getTable(table, index, count)
    # Check if the input is a pandas DataFrame
    if not isinstance(table, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    json_str = ""
    
    for row in table.itertuples(index=False):
        # Convert the row to a dictionary
        row_dict = row._asdict()
        
        json_str += json.dumps(row_dict) + "\n"
    
    return json_str.strip()  # Remove the trailing newline if present
    

def getTableString(table):
    return table.to_json(orient='records', lines=True)
    #tabulate(table, headers='keys', tablefmt='psql', showindex=False)

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
    json_row = {column:item for item,column in zip(new_row, new_columns)}
    return f"""
Elements:{' '.join(new_row)}
JSON:{json_row}
    """

def getExamples(table, count=3, percentage=0.8):
    examples = ""
    columns = table.columns.to_list()
    for i in range(count):
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
        
    