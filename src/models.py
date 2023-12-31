import os
import json
import pandas as pd
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
from src.utils import (getExamples, getRow, dict2row, getRowDF, 
                       getTableString, prepareDFForCell, prepareDFForCellV2,
                       getMappingFromRowResult, getColumnGroups)
from src import prompts
import ast
import math

class BaseModel:
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base="",
                 system_template="", 
                 human_template="",
                 is_json = True,
                 name="Base Model"
                 ):
        if model_name == "finetuned_model":
            model_name = "ft:gpt-3.5-turbo-0613:invesya::8EIwnib4"
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=openai_api_key,
            temperature=0,
            openai_api_base=openai_api_base,
            request_timeout=120
        )
        self.name=name
        self.is_json = is_json
        self.initChain(system_template, human_template)
        
    def initChain(self, system_template="", human_template=""):
        prompts = []
        if system_template:
            prompts.append(SystemMessagePromptTemplate.from_template(system_template))
        if human_template:
            prompts.append(HumanMessagePromptTemplate.from_template(human_template))
        chat_prompt = ChatPromptTemplate.from_messages(prompts)
        self.chain =  LLMChain(llm=self.llm, prompt=chat_prompt)
        print(f"{self.name} has been successfully initialized.")
        
    def refineJson(self, json_string):
        if "{" not in json_string or "}" not in json_string:
            return "{}"
        start_index = json_string.find("{")
        end_index = json_string.rfind("}") + 1
        return json_string[start_index:end_index]
        
    def __call__(self, **kwargs):
        res = self.chain.run(**kwargs)
        if self.is_json:
            res = self.refineJson(res)
        if self.is_json:
            try:
                res = json.loads(res)
            except json.JSONDecodeError:
                try:
                    res = ast.literal_eval(res)
                except (SyntaxError, ValueError):
                    print("Failed to decode input string")
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
                         human_template = prompts.row.human_template,
                         name="Row Model"
                         )
        
    def __call__(self, **kwargs):
        res = super().__call__(**kwargs)
        res = {k:v for k, v in res.items() if v}
        target_columns = kwargs.get('columns')
        new_row = {}
        for col in target_columns:
            if col not in res:
                new_row[col] = ""
            else:
                new_row[col] = res[col]

        return new_row

class ColumnTransformerModel(BaseModel):
    """It gets a source row and couple of target rows then using few shot learning, it changes the keys of the source.
    It results in an intermediate result for a single row where the values might not fit the target JSON but keys should. 
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.column_transformation.system_template,
                         human_template = prompts.column_transformation.human_template,
                         name="Column Transformer Model"
                         )
        
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
                         human_template = prompts.cell.human_template,
                         name="Cell Model"
                         )
        
class CellModelV2(BaseModel):
    """It gets intermediate row and couple of target rows for few shot learning.
    Intermediate row and the target rows have the same columns.
    Some of the intermediate rows might be empty which is also handled.
    According to the target rows, assistant generates a valid rows without column names.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.cell_v2.system_template,
                         human_template = prompts.cell_v2.human_template,
                         name="Cell Model V2"
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
                         human_template = prompts.column_mappings.human_template,
                         name="Column Mapping Model"
                         )
        
    def __call__(self, **kwargs):
        array1 = kwargs["array1"]
        array2 = kwargs["array2"]
        kwargs["array1"] = array1.iloc[0].values
        kwargs["array2"] = array2.iloc[0].values
        res = super().__call__(self, **kwargs)
        res = getMappingFromRowResult(res, array1, array2)
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
                         human_template = prompts.applier.human_template,
                         name="Applier Model"
                         )
        
    def refine(self, res):
        """In case the generated JSON is not valid.
        """
        max_count = 0
        for v in res.values():
            count = len(v)
            max_count = max(max_count, count)
        
        for k,v in res.items():
            extra = max_count - len(v)
            if extra > 0:
                extra_items = extra * ['']
                v += extra_items
                res[k] = v
        
        return res
                  
        
    def __call__(self, **kwargs):
        res = super().__call__(**kwargs)
        res = self.refine(res)
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
                         human_template = prompts.feedback_row.human_template,
                         name="Feedback Row Model"
                         )
        
    def __call__(self,**kwargs):
        res = super().__call__(**kwargs)
        columns = kwargs.get('columns', [])
        return {k:v for k,v in res.items() if k in columns}
    
class FeedbackCellModel(BaseModel):
    """By looking at the feedback coming from the user for the first row, generate the refined version.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.feedback_cell.system_template,
                         human_template = prompts.feedback_cell.human_template,
                         name="Feedback Cell Model"
                         )
        
    def __call__(self, **kwargs):
        res = super().__call__(self, **kwargs)
        columns = kwargs["columns"]
        for col in columns:
            if col not in res:
                res[col] = ""
        for k,v in res.items():
            res[k] = [v]
        return pd.DataFrame.from_dict(res)
    
class Json2ParagraphModel(BaseModel):
    """By looking at the feedback coming from the user for the first row, generate the refined version.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.json2paragraph.system_template,
                         human_template = prompts.json2paragraph.human_template,
                         is_json=False,
                         name="JSON To Paragraph Model"
                         )    

class Json2ParagraphSourceModel(BaseModel):
    """By looking at the feedback coming from the user for the first row, generate the refined version.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.json2paragraph_source.system_template,
                         human_template = prompts.json2paragraph_source.human_template,
                         is_json=False,
                         name="JSON To Paragraph Source Model"
                         )
        
class Paragraph2JsonModel(BaseModel):
    """By looking at the feedback coming from the user for the first row, generate the refined version.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.paragraph2json.system_template,
                         human_template = prompts.paragraph2json.human_template,
                         name="Paragraph To JSON Model"
                         )
    
class RefinerModel(BaseModel):
    """By looking at the feedback coming from the user for the first row, generate the refined version.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.refiner.system_template,
                         human_template = prompts.refiner.human_template,
                         name="Refiner Model"
                         )
        self.paragraph2json_model = Paragraph2JsonModel(model_name, 
                                                        openai_api_key, 
                                                        openai_api_base)
        self.json2paragraph_model = Json2ParagraphModel(model_name, 
                                                        openai_api_key, 
                                                        openai_api_base)
        
    def __call__(self, source_json, target_json, intermediate_json):
        missing_keys = [k for k,v in intermediate_json.items() if not v]
        target_paragraph =  self.json2paragraph_model(data=target_json)
        target_json = {k:target_json[k] for k in missing_keys}
        non_missing_source_json = {k:v for k,v in source_json.items() if v}
        source_paragraph = self.json2paragraph_model(data=non_missing_source_json)
        
        try:
            new_source_json = self.paragraph2json_model(target_paragraph=target_paragraph,
                                                        target_json=target_json,
                                                        source_paragraph=source_paragraph,
                                                        columns=missing_keys)
            for k,v in new_source_json.items():
                if v:
                    intermediate_json[k] = v
        except Exception as e:
            print(e)
            
        return intermediate_json
    
class ColumnRenamerModel(BaseModel):
    """It generates a new column names for the given table.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.column_renamer.system_template,
                         human_template = prompts.column_renamer.human_template,
                         name="Column Renamer Model"
                         )

class TargetTablePatternFinderModel(BaseModel):
    """It finds the patterns of the given table.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.target_table_pattern_finder.system_template,
                         human_template = prompts.target_table_pattern_finder.human_template,
                         is_json=False,
                         name="Target Table Pattern Finder Model"
                         )
        
class TargetTablePatternApplierModel(BaseModel):
    """It applies the patterns to the other table.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.target_table_pattern_applier.system_template,
                         human_template = prompts.target_table_pattern_applier.human_template,
                         name="Target Table Pattern Applier Model"
                         )

class FinetunedModel(BaseModel):
    """Finetuned Model
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.finetuned.system_template,
                         human_template = prompts.finetuned.human_template,
                         name="Finetuned Model"
                         )       
    
class ModelManager:
    def __init__(self,
                 model_name, 
                 openai_api_key, 
                 openai_api_base,
                 source=None,
                 target=None,
                 CELL_LIMIT=50):
        self.row_model = RowModel(model_name=model_name, 
                                  openai_api_key=openai_api_key, 
                                  openai_api_base=openai_api_base)
        
        self.cell_model = CellModel(model_name=model_name, 
                                    openai_api_key=openai_api_key, 
                                    openai_api_base=openai_api_base)
        
        self.cell_model_v2 = CellModelV2(model_name=model_name, 
                                    openai_api_key=openai_api_key, 
                                    openai_api_base=openai_api_base)
        
        self.column_mappings_model = ColumnMappingsModel(model_name=model_name, 
                                              openai_api_key=openai_api_key, 
                                              openai_api_base=openai_api_base)
        
        self.applier_model = ApplierModel(model_name=model_name, 
                                          openai_api_key=openai_api_key, 
                                          openai_api_base=openai_api_base)
        
        self.feedback_row_model = FeedbackRowModel(model_name=model_name, 
                                               openai_api_key=openai_api_key, 
                                               openai_api_base=openai_api_base)
        
        self.feedback_cell_model = FeedbackCellModel(model_name=model_name, 
                                               openai_api_key=openai_api_key, 
                                               openai_api_base=openai_api_base)
        
        self.refiner_model = RefinerModel(model_name=model_name, 
                                          openai_api_key=openai_api_key, 
                                          openai_api_base=openai_api_base)
        
        self.json2paragraph_model = Json2ParagraphModel(model_name, 
                                                        openai_api_key, 
                                                        openai_api_base)
        
        self.json2paragraph_source_model = Json2ParagraphSourceModel(model_name, 
                                                              openai_api_key, 
                                                              openai_api_base)
        
        self.column_transformer_model = ColumnTransformerModel(model_name=model_name, 
                                                               openai_api_key=openai_api_key, 
                                                               openai_api_base=openai_api_base)
        
        self.column_renamer_model = ColumnRenamerModel(model_name=model_name, 
                                                       openai_api_key=openai_api_key, 
                                                       openai_api_base=openai_api_base)
        
        self.target_table_pattern_finder_model = TargetTablePatternFinderModel(model_name=model_name, 
                                                                               openai_api_key=openai_api_key, 
                                                                               openai_api_base=openai_api_base)
        
        self.target_table_pattern_applier_model = TargetTablePatternApplierModel(model_name=model_name, 
                                                                                 openai_api_key=openai_api_key, 
                                                                                 openai_api_base=openai_api_base)
        
        self.finetuned_model = FinetunedModel(model_name=model_name, 
                                              openai_api_key=openai_api_key, 
                                              openai_api_base=openai_api_base)
        
        self.target_column_threshold = 20       # it is used to decide for the algorithm used in few shot prompt preparation.
        self.high_target_column_mapping = 30    # it is used to decide for the example count for CellModel
        self.source = source
        self.target=target
        if self.target is not None:
            self.original_columns = self.target.columns
            self.target, self.identical_columns = getColumnGroups(self.target)
            self.target.fillna("",inplace=True)
            # Convert all Timestamp columns to string
            for col in self.target.select_dtypes(include=["datetime"]).columns:
                self.target[col] = self.target[col].astype(str)
            for col in self.source.select_dtypes(include=["datetime"]).columns:
                self.source[col] = self.source[col].astype(str)
        
        self.CELL_LIMIT = CELL_LIMIT            # it is used for number of cell generation during the completion of the whole table
            
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
        self.target.fillna("",inplace=True)
        
        # Convert all Timestamp columns to string
        for col in self.target.select_dtypes(include=["datetime"]).columns:
            self.target[col] = self.target[col].astype(str)
        for col in self.source.select_dtypes(include=["datetime"]).columns:
            self.source[col] = self.source[col].astype(str)
        
        if self.source is not None:
            self.SOURCE_ROW_PERIOD = max(1, self.CELL_LIMIT // self.source.shape[1])
        else:
            self.SOURCE_ROW_PERIOD = None
            
        if self.target is not None:
            self.original_columns = self.target.columns
            self.target, self.identical_columns = getColumnGroups(self.target)
        
    def getConfirmationMessage_old(self):
        self.examples, self.target_columns = getExamples(self.target,
                                        self.ROW_MODEL_FEW_SHOT_COUNT,
                                        self.ROW_MODEL_PERCENTAGE)
        
        self.source_first_row_str = getRow(self.source,0)
        self.transformed_source_first_row_json = self.row_model(examples=self.examples, columns=self.target_columns, row=self.source_first_row_str)
        transformed_source_first_row_df = dict2row(self.transformed_source_first_row_json)
        row = getRowDF(self.source,0)
        # source_fst_row_str_in_table = getTableString(row)
        # transformed_source_fst_row_str_in_table = getTableString(transformed_source_first_row_df)
        self.stage = 1
        self.mappings = self.column_mappings_model(array1=row, 
                                                   array2=transformed_source_first_row_df)
        return self.mappings
    
    def getConfirmationMessage(self):           
        self.examples, self.target_columns = getExamples(self.target)
        
        self.source_first_row_str = getRow(self.source,0,self.target.shape[0])
        self.transformed_source_first_row_json = self.row_model(examples=self.examples, columns=self.target_columns, row=self.source_first_row_str)
        reformatted_row_json = self.cell_model(table1=self.transformed_source_first_row_json,
                                               table2=prepareDFForCell(self.target,0),
                                               columns=self.target_columns)
        for col in self.target_columns:
            if not self.transformed_source_first_row_json.get(col):
                reformatted_row_json[col] = ""
                
        """reformatted_row_json = self.refiner_model(source_json=self.source.iloc[0].to_dict(),
                                              target_json=self.target.iloc[-1].to_dict(),
                                              intermediate_json = reformatted_row_json)"""
                
        transformed_df = dict2row(reformatted_row_json)
        for k,cols in self.identical_columns.items():
            for col in cols:
                if col not in transformed_df.columns:
                    transformed_df[col] = transformed_df[k]
        self.transformed_df = transformed_df[self.original_columns]
        row = getRowDF(self.source,0)
        return {
            "previous":row,
            "after":self.transformed_df
        }
        
    def getConfirmationMessageV2(self):
        try:
            self.target_column_mapping = self.column_transformer_model(columns=list(self.target.columns),
                                                                       row=self.target.iloc[0])
        except Exception as e:
            print("Target Column Mapping failed")
            print(e)
            self.target_column_mapping = {col:col for col in self.target.columns}
            
        self.examples, self.target_columns = getExamples(self.target)
        
        self.source_first_row_str = getRow(self.source,0)
        self.transformed_source_first_row_json = self.row_model(examples=self.examples, columns=self.target_columns, row=self.source_first_row_str)
        table1 = {str(k):self.transformed_source_first_row_json.get(self.target.columns[k],'') for k in range(self.target.shape[1])}
        reformatted_row_json_index_based = self.cell_model_v2(table1=table1,
                                                  table2=prepareDFForCellV2(self.target,1,self.CELL_MODEL_EXAMPLES_COUNT),
                                                  columns=[str(k) for k in range(self.target.shape[1])])
        reformatted_row_json = {}
        
        for k in range(self.target.shape[1]):
            res = reformatted_row_json_index_based.get(str(k),'')
            col = self.target.columns[k]
            if not self.transformed_source_first_row_json.get(col):
                reformatted_row_json[col] = ""
            else:
                reformatted_row_json[col] = res     
                
        print(reformatted_row_json)           
                
        transformed_df = dict2row(reformatted_row_json)
        for k,cols in self.identical_columns.items():
            for col in cols:
                if col not in transformed_df.columns:
                    transformed_df[col] = transformed_df[k]
        self.transformed_df = transformed_df[self.original_columns]
        row = getRowDF(self.source,0)
        return {
            "previous":row,
            "after":self.transformed_df
        }
        
    def getExamples(self, example_count = 3):
        example_count = min(self.target.shape[0]-1, example_count)
        examples = ""
        for i in range(1,example_count+1):
            row = self.target.iloc[i].to_dict()
            paragraph = self.json2paragraph_model(data = row)
            example = f"""
Source: {paragraph}

JSON:{row}            
            """
            examples += example + "\n"
        
        return examples , self.target.columns.to_list(), paragraph, row
    
    def getRow(self, index=0, example_paragraph="", example_json={}):
        row = self.source.iloc[index].to_dict()
        return self.json2paragraph_source_model(data = row, 
                                                example_paragraph=example_paragraph,
                                                example_json=example_json)
    
    def prepareDFForCell(self, index=0, count=3):
        table_dict_list = self.target.to_dict('records')
        table_dict_list = table_dict_list[index:index+count] # even if there is an out of bound, it is still safe
        system_in = ""
        keys = table_dict_list[0].keys()
        for key in keys:
            report = f"Key:{key}\nExamples:"
            found = False
            for table_dict in table_dict_list:
                if table_dict[key]:
                    found = True
                    report += str(table_dict[key]) + ", " 
            if found:
                report = report[:-2]
                system_in += report + "\n\n"
        return system_in.strip()
            
    def getConfirmationMessageV3(self): 
        column_mapping = self.column_renamer_model(column_names=self.target.columns.tolist(), rows=self.target.iloc[:2].to_json()) 
        reverse_column_mapping = {v:k for k, v in column_mapping.items()}
        self.target.rename(columns=column_mapping, inplace=True)
        self.examples, self.target_columns, example_paragraph, example_json = self.getExamples(example_count=3)
        
        self.source_first_row_str = self.getRow(example_paragraph=example_paragraph, example_json=example_json)
        self.transformed_source_first_row_json = self.row_model(examples=self.examples, columns=self.target_columns, row=self.source_first_row_str)
        
        patterns = self.target_table_pattern_finder_model(examples=self.prepareDFForCell(1))
        reformatted_row_json = self.target_table_pattern_applier_model(patterns=patterns, json=self.transformed_source_first_row_json)

        for col in self.target_columns:
            if not self.transformed_source_first_row_json.get(col):
                reformatted_row_json[col] = ""
                
        transformed_df = dict2row(reformatted_row_json)
        transformed_df.rename(columns=reverse_column_mapping, inplace=True)
        self.target.rename(columns=reverse_column_mapping, inplace=True)
        for k,cols in self.identical_columns.items():
            for col in cols:
                if col not in transformed_df.columns:
                    transformed_df[col] = transformed_df[k]
        self.transformed_df = transformed_df[self.original_columns]
        row = getRowDF(self.source,0)
        return {
            "previous":row,
            "after":self.transformed_df
        }
        
    def refine_old(self, feedback):
        self.transformed_source_first_row_json = self.feedback_row_model(columns=self.target_columns, 
                                                                     source_json=self.source.iloc[0].to_json(),
                                                                     result_json=self.transformed_source_first_row_json,
                                                                     relations=self.mappings,
                                                                     feedback=feedback)
        transformed_source_first_row_df = dict2row(self.transformed_source_first_row_json)
        row = getRowDF(self.source,0)
        # source_fst_row_str_in_table = getTableString(row)
        # transformed_source_fst_row_str_in_table = getTableString(transformed_source_first_row_df)
        self.stage = 1
        self.mappings = self.column_mappings_model(array1=row, 
                                           array2=transformed_source_first_row_df)

        return self.mappings
    
    def refine(self, feedback):
        self.transformed_source_first_row_json = self.feedback_cell_model(columns=self.target_columns, 
                                                                     source_json=self.source.iloc[0].to_json(),
                                                                     result_json=self.transformed_source_first_row_json,
                                                                     feedback=feedback)
        transformed_source_first_row_df = dict2row(self.transformed_source_first_row_json)
        row = getRowDF(self.source,0)
        # source_fst_row_str_in_table = getTableString(row)
        # transformed_source_fst_row_str_in_table = getTableString(transformed_source_first_row_df)
        self.stage = 1
        self.mappings = self.column_mappings_model(array1=row, 
                                                   array2=transformed_source_first_row_df)

        return self.mappings
    
    def getTableWithFinetunedModel(self):
        examples = self.target.iloc[:3].to_dict()
        examples_str = json.dumps(examples)
        rows = []
        for i in range(self.source.shape[0]):
            row = self.source.iloc[i].to_dict()
            row = json.dumps(row)
            result = self.finetuned_model(examples_str=examples_str,
                                          source_str=row)
            rows.append(result)
            yield i, int(100*i/self.source.shape[0])
            
        table = pd.DataFrame(rows)
        for k,cols in self.identical_columns.items():
            for col in cols:
                if col not in table.columns:
                    table[col] = table[k]
        table.fillna("",inplace=True)
        yield table[self.original_columns], 100
            
        
    def getTable(self, gt_row=None):
        if gt_row is None:
            gt_row = self.transformed_df   
        first_row = gt_row.iloc[0]
        json_str = first_row.to_json()
        target_json = json.loads(json_str)
        target_json = {k:[v] for k,v in target_json.items() if k in self.target.columns}    

        source_json = getRowDF(self.source,0).to_dict()
        
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
        combined_table.fillna("",inplace=True)
        yield combined_table[self.original_columns], 100
        self.stage = 2                