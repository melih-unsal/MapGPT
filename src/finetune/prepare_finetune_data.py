import os
import os.path as osp
import json
import random
from collections import defaultdict 
import pandas as pd
import args
import utils
from tqdm import tqdm
from tabulate import tabulate
import tiktoken

encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')

token = 0


# Get column mappings with 2 ways (source-target and target-source)
column_mapping_data = {}
for filename in os.listdir(args.COLUMN_MAPPING_ROOT):
    filepath = osp.join(args.COLUMN_MAPPING_ROOT, filename)
    index = filename.split(".")[0]
    df = pd.read_csv(filepath)
    source_to_target_correspondance = df.iloc[0].to_dict()
    
    target_to_source_correspondance = defaultdict(list)
    for k,v in source_to_target_correspondance.items():
        if v:
            target_to_source_correspondance[v].append(k)
    
    source_to_target_correspondance = {k:[v] for k,v in source_to_target_correspondance.items()}
    
    column_mapping_data[index] = {
        "source_to_target":source_to_target_correspondance,
        "target_to_source":dict(target_to_source_correspondance)
    }
    
finetune_data_train = open("train1_small.jsonl", "w")
finetune_data_val = open("val1_small.jsonl", "w")
    
for filename in tqdm(os.listdir(args.ORIGINAL_DATA_ROOT)):
    filepath = osp.join(args.ORIGINAL_DATA_ROOT, filename)
    file_index, file_type = filename.split('.')[0].split("_")
    
    # Check if extracted file type is valid
    if file_type not in ['source', 'target']:
        continue
    # Determine the other file type
    other_type = 'target' if file_type == 'source' else 'source'
    other_filename = f"{file_index}_{file_type}_to_{other_type}.csv"
    other_filepath = osp.join(args.TARGET_ROOT, other_filename)
    
    source_data = pd.read_csv(filepath)
    source_data.fillna("",inplace=True)
    target_data = pd.read_csv(other_filepath)
    target_data.fillna("",inplace=True)
    
    if 'Unnamed: 0' in source_data.columns:
        source_data = source_data.drop(columns='Unnamed: 0')
    if 'Unnamed: 0' in target_data.columns:
        target_data = target_data.drop(columns='Unnamed: 0')
    
    assert source_data.shape[0] == target_data.shape[0]
    
    # First prepare source to target data
    
    column_mapping = column_mapping_data[file_index][f"{other_type}_to_{file_type}"]
    
    for row_index in range(source_data.shape[0]):
        for _ in range(args.EXAMPLE_PER_ROW):
            source_columns, target_columns = utils.selectColumns(source_data.columns, target_data.columns)
            
            all_target_indices = list(range(row_index)) + list(range(row_index + 1,target_data.shape[0]))
            selected_example_indices = random.sample(all_target_indices, min(target_data.shape[0],args.TARGET_ROW_PER_SOURCE_ROW))
            
            example_json  = target_data.loc[selected_example_indices,target_columns].to_dict()
            source_json   = source_data.loc[row_index,source_columns].to_dict()
            target_json   = target_data.loc[row_index,target_columns].to_dict()
            target_json = utils.finalize(source_json, target_json, column_mapping) 
            
            # shuffle the keys randomly
            source_key_correspondance = utils.getKeyCorrespondance(source_json)
            target_key_correspondance = utils.getKeyCorrespondance(target_json)
            
            source_json = {source_key_correspondance[k]:v for k, v in source_json.items()}
            target_json = {target_key_correspondance[k]:v for k, v in target_json.items()}
            example_json = {target_key_correspondance[k]:v for k, v in example_json.items()}

            examples_str = json.dumps(example_json)
            source_str = json.dumps(source_json)
            target_str = json.dumps(target_json)
            
            user_content = f"""Examples:
{examples_str}
        
Source JSON:
{source_str}
            """
            assistant_content = target_str
            messages = [
                {"role": "system", "content":args.SYSTEM_MESSAGE},
                {"role": "user", "content":user_content},
                {"role": "assistant", "content":assistant_content}
            ]
            data = {"messages": messages}
            data_str = json.dumps(data)
            if int(file_index) < 13:
                finetune_data_train.write(data_str + "\n")
            else:
                finetune_data_val.write(data_str + "\n")
            token += len(encoding.encode(data_str))
        break


finetune_data_train.close()
finetune_data_val.close()
print("token",token)