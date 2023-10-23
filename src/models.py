import os
import json
import pandas as pd
from termcolor import colored
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
from pathlib import Path
from src.utils import (getExamples, getRow, dict2row, getRowDF, 
                       getTable, getTableString, prepareDFForCell, 
                       getTargetCols, getMappingFromRowResult, getColumnGroups)
from src import prompts
import ast
import math

class BaseModel:
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base="",
                 system_template="", 
                 human_template="",
                 ):
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=openai_api_key,
            temperature=0,
            openai_api_base=openai_api_base
        )
        self.initChain(system_template, human_template)
        
    def initChain(self, system_template="", human_template=""):
        prompts = []
        if system_template:
            prompts.append(SystemMessagePromptTemplate.from_template(system_template))
        if human_template:
            prompts.append(HumanMessagePromptTemplate.from_template(human_template))
        chat_prompt = ChatPromptTemplate.from_messages(prompts)
        self.chain =  LLMChain(llm=self.llm, prompt=chat_prompt)
        print("LLMChain has been successfully initialized.")
        
    def __call__(self, is_json=True, **kwargs):
        res = self.chain.run(**kwargs)
        if is_json:
            res = ast.literal_eval(res)
        print(colored(res,"blue"))
        return res

class RowModel(BaseModel):
    """It gets a source row and couple of target rows then using few shot learning, it changes the keys of the source.
    It results in an intermediate result for a single row where the values might not fit the target JSON but keys should. 
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.row.system_template,
                         human_template = prompts.row.human_template
                         )
        
    def __call__(self, **kwargs):
        new_row = super().__call__(**kwargs)
        print(colored(new_row,"green"))
        new_row = {k:v for k, v in new_row.items() if v}
        target_columns = kwargs.get('columns')
        for col in target_columns:
            if col not in new_row:
                new_row[col] = ""

        return new_row
        
class CellModel(BaseModel):
    """It gets intermediate row and couple of target rows for few shot learning.
    Intermediate row and the target rows have the same columns.
    Some of the intermediate rows might be empty which is also handled.
    According to the target rows, assistant generates a valid JSON which is ready to be transformed to dataframe

    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.cell.system_template,
                         human_template = prompts.cell.human_template
                         )
    
class ColumnMappingsModel(BaseModel):
    """It explains the transformation made in the original table to inform the user.
    According to the validation result coming from the user, refining the mapping might be needed.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.column_mappings.system_template,
                         human_template = prompts.column_mappings.human_template
                         )
        
    def __call__(self, **kwargs):
        array1 = kwargs["array1"]
        array2 = kwargs["array2"]
        print("df1:")
        print(array1)
        print("df2:")
        print(array2)
        kwargs["array1"] = array1.iloc[0].values
        kwargs["array2"] = array2.iloc[0].values
        res = super().__call__(self, **kwargs)
        res = getMappingFromRowResult(res, array1, array2)
        print("res:")
        print(res)
        return res
        
class ApplierModel(BaseModel):
    """By looking at the transformation of a single row, it applies the same transformation
    for the other given rows.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.applier.system_template,
                         human_template = prompts.applier.human_template
                         )
        
    def __call__(self, **kwargs):
        res = super().__call__(**kwargs)
        return pd.DataFrame.from_dict(res)
    
class FeedbackRowModel(BaseModel):
    """By looking at the feedback coming from the user it refines the row model's result.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.feedback_row.system_template,
                         human_template = prompts.feedback_row.human_template
                         )
        
    def __call__(self,**kwargs):
        res = super().__call__(**kwargs)
        columns = kwargs.get('columns', [])
        return {k:v for k,v in res.items() if k in columns}
    
class ModelManager:
    def __init__(self,
                 model_name, 
                 openai_api_key, 
                 openai_api_base,
                 source="",
                 target="",
                 CELL_LIMIT=200):
        self.row_model = RowModel(model_name=model_name, 
                                  openai_api_key=openai_api_key, 
                                  openai_api_base=openai_api_base)
        self.cell_model = CellModel(model_name=model_name, 
                                    openai_api_key=openai_api_key, 
                                    openai_api_base=openai_api_base)
        self.column_mappings_model = ColumnMappingsModel(model_name=model_name, 
                                              openai_api_key=openai_api_key, 
                                              openai_api_base=openai_api_base)
        self.applier_model = ApplierModel(model_name=model_name, 
                                          openai_api_key=openai_api_key, 
                                          openai_api_base=openai_api_base)
        
        self.feedback_model = FeedbackRowModel(model_name=model_name, 
                                               openai_api_key=openai_api_key, 
                                               openai_api_base=openai_api_base)
        self.source = source
        self.target=target
        if self.target is not None:
            self.original_columns = self.target.columns
            self.target, self.identical_columns = getColumnGroups(self.target)
        self.ROW_MODEL_FEW_SHOT_COUNT = 6 # it is the few shot example count for row model 
        self.ROW_MODEL_PERCENTAGE = 0.6
        self.CELL_MODEL_EXAMPLES_COUNT = 5
        self.CELL_LIMIT = CELL_LIMIT
        self.stage = 0
        
        if self.source is not None:
            self.SOURCE_ROW_PERIOD = max(1, self.CELL_LIMIT // self.source.shape[1])
        else:
            self.SOURCE_ROW_PERIOD = None
            
    @property
    def iterCount(self):
        if self.SOURCE_ROW_PERIOD is not None:
            return math.ceil(self.source.shape[0]/self.SOURCE_ROW_PERIOD)
        return 0
        
    
    def setTables(self, source, target):
        self.source = source
        self.target = target
        
        if self.source is not None:
            self.SOURCE_ROW_PERIOD = max(1, self.CELL_LIMIT // self.source.shape[1])
        else:
            self.SOURCE_ROW_PERIOD = None
            
        if self.target is not None:
            self.original_columns = self.target.columns
            self.target, self.identical_columns = getColumnGroups(self.target)
        
    def getConfirmationMessage(self):
        self.examples, self.target_columns = getExamples(self.target,
                                        self.ROW_MODEL_FEW_SHOT_COUNT,
                                        self.ROW_MODEL_PERCENTAGE)
        
        self.source_first_row_str = getRow(self.source,0)
        self.transformed_source_first_row_json = self.row_model(examples=self.examples, columns=self.target_columns, row=self.source_first_row_str)
        transformed_source_first_row_df = dict2row(self.transformed_source_first_row_json)
        row = getRowDF(self.source,0)
        source_fst_row_str_in_table = getTableString(row)
        transformed_source_fst_row_str_in_table = getTableString(transformed_source_first_row_df)
        self.stage = 1
        self.mappings = self.column_mappings_model(array1=row, 
                                    array2=transformed_source_first_row_df)
        return self.mappings
        
    def refine(self, feedback):
        self.transformed_source_first_row_json = self.feedback_model(columns=self.target_columns, 
                                                                     source_json=self.source.iloc[0].to_json(),
                                                                     result_json=self.transformed_source_first_row_json,
                                                                     relations=self.mappings,
                                                                     feedback=feedback)
        transformed_source_first_row_df = dict2row(self.transformed_source_first_row_json)
        row = getRowDF(self.source,0)
        source_fst_row_str_in_table = getTableString(row)
        transformed_source_fst_row_str_in_table = getTableString(transformed_source_first_row_df)
        self.stage = 1
        self.mappings = self.column_mappings_model(array1=row, 
                                           array2=transformed_source_first_row_df)

        return self.mappings
        
    def getTable(self):       
        reformatted_row_json = self.cell_model(table1=self.transformed_source_first_row_json,
                                               table2=prepareDFForCell(self.target,0,self.CELL_MODEL_EXAMPLES_COUNT),
                                               columns=self.target_columns)
        for col in self.target_columns:
            if not self.transformed_source_first_row_json.get(col):
                reformatted_row_json[col] = {0:""}
            else:
                reformatted_row_json[col] = {0:reformatted_row_json[col]}
                
        #source_json = {k:v for k,v in getRowDF(self.source,0).to_dict().items() if k in self.mappings}
        source_json = getRowDF(self.source,0).to_dict()
        target_cols = getTargetCols(self.mappings)
        target_json = {k:v for k,v in reformatted_row_json.items() if k in target_cols or k in self.target.columns}
        
        combined_table = pd.DataFrame(columns=self.target.columns)
        
        for start_index in range(0,self.source.shape[0],self.SOURCE_ROW_PERIOD):
            end_index = min(start_index + self.SOURCE_ROW_PERIOD, self.source.shape[0])       
            #dataframe_json = {k:v for k,v in self.source.iloc[start_index:end_index].to_dict().items() if k in self.mappings}
            dataframe_json = self.source.iloc[start_index:end_index].to_dict()
            portion_table = self.applier_model(
                source_json=source_json,
                target_json=target_json,
                dataframe_json=dataframe_json,
            )
            combined_table = pd.concat([combined_table, portion_table], ignore_index=True)
            yield combined_table, min(99, int(100*end_index/self.source.shape[0]))     
        # put identical columns here
        for k,cols in self.identical_columns.items():
            for col in cols:
                if col not in combined_table.columns:
                    combined_table[col] = combined_table[k]
        yield combined_table[self.original_columns], 100
        self.stage = 2                