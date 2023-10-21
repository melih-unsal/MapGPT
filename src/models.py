import os
import json
import pandas as pd
from termcolor import colored
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
import prompts
from utils import getTableString
import ast

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
    
class ExplainerModel(BaseModel):
    """It explains the transformation made in the original table to inform the user.
    According to the validation result coming from the user, refining the mapping might be needed.
    """
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.explainer.system_template,
                         human_template = prompts.explainer.human_template
                         )
        
    def __call__(self, **kwargs):
        return super().__call__(is_json=False, **kwargs)
        
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
        table = pd.DataFrame.from_dict(res)
        print(getTableString(table))
        return table
        
class FinalizerModel(BaseModel):
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.finalizer.system_template,
                         human_template = prompts.finalizer.human_template
                         )
        
    def __call__(self, **kwargs):
        res = super().__call__(**kwargs)
        return pd.DataFrame.from_dict(res)
    
class ModelManager:
    def __init__(self):
        self.row_model = RowModel()
        self.cell_model = CellModel()
        self.finalizer_model = FinalizerModel()
        self.FEW_SHOT_EXAMPLE_COUNTS={}