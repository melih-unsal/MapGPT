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
from utils import dict2row

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
        
    def __call__(self, **kwargs):
        return self.chain.run(**kwargs)

class RowModel(BaseModel):
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
        res = super().__call__(**kwargs).replace("\'", "\"")
        print(colored(res,"green"))
        new_row = json.loads(res)
        new_row = {k:v for k, v in new_row.items() if v}
        target_columns = kwargs.get('columns')
        for col in target_columns:
            if col not in new_row:
                new_row[col] = [""]
            else:
                new_row[col] = [new_row[col]]

        return new_row
        
class CellModel(BaseModel):
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.cell.system_template,
                         human_template = prompts.cell.human_template
                         )
        
    def __call__(self, **kwargs):
        res = super().__call__(**kwargs)    
        res = res.replace("'",'"')
        df_json = json.loads(res)
        return dict2row(df_json)
    
class ExplainerModel(BaseModel):
    def __init__(self, model_name="gpt-3.5-turbo", 
                 openai_api_key = os.getenv("OPENAI_API_KEY",""),
                 openai_api_base=""):
        super().__init__(model_name, 
                         openai_api_key, 
                         openai_api_base,
                         system_template = prompts.explainer.system_template,
                         human_template = prompts.explainer.human_template
                         )
        
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
        res = super().__call__(**kwargs).replace("\'", "\"")
        df_json = json.loads(res)
        return pd.DataFrame.from_dict(df_json)
    
    
class ModelManager:
    def __init__(self):
        self.row_model = RowModel()
        self.cell_model = CellModel()
        self.finalizer_model = FinalizerModel()
        self.FEW_SHOT_EXAMPLE_COUNTS={}