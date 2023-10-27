import args
import random

def selectColumns(source_columns, target_columns):
    source_columns = list(source_columns)
    target_columns = list(target_columns)
    
    if random.random() < args.DELETE_PROB:
        delete_percetange = args.DELETE_PERCENTAGE_LIMIT * random.random()
        delete_source_count = int(delete_percetange * len(source_columns))
        remaining_source_count = len(source_columns) - delete_source_count
        source_columns = random.sample(source_columns, remaining_source_count)
        
    if random.random() < args.DELETE_PROB:
        delete_percetange = args.DELETE_PERCENTAGE_LIMIT * random.random()
        delete_target_count = int(delete_percetange * len(target_columns))
        remaining_target_count = len(target_columns) - delete_target_count
        target_columns = random.sample(target_columns, remaining_target_count)
    
    return source_columns, target_columns

def finalize(source_json, target_json, column_mapping):
    source_cols = set(source_json.keys())
    for k in target_json.keys():
        if any([col not in source_cols for col in column_mapping.get(k,[])]):
            target_json[k] = ""
    return target_json
    
def getKeyCorrespondance(data):
    if random.random() < args.SHUFFLE_COLUMNS_PROB:
        original_keys = list(data.keys())
        shuffled_keys = original_keys.copy()
        random.shuffle(shuffled_keys)
        return {k:v for k,v in zip(original_keys,shuffled_keys)}

    return {k:k for k in data.keys()}
    
                    