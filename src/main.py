from pathlib import Path
from utils import getExamples, getRow, dict2row, getRowDF, getTable, getTableString
from models import RowModel, CellModel, ExplainerModel, FinalizerModel
import os

root_folder = os.path.join(Path(__file__).parent.parent,"data")

source_path = os.path.join(root_folder, "table_A.csv")
source_path = "/home/melih/Desktop/personal/others/langchain/tests/unit_tests/document_loaders/test_docs/csv/test_one_col.csv"
target_path = os.path.join(root_folder, "template.csv")

examples, columns = getExamples(target_path,6,0.4)

# INITIALIZE MODELS
row_model = RowModel()
cell_model = CellModel()
explainer_model = ExplainerModel()
finalizer_model = FinalizerModel()


row = getRow(source_path,0)
transformed_row = row_model(examples=examples, columns=columns, row=row)
df_row = dict2row(transformed_row)
print("--------------------------------FIRST ROW--------------------------------")
print(df_row)

print("--------------------------------EXPLANATION--------------------------------")

row1 = getRowDF(source_path,0)
row1 = getTableString(row1)
row2=df_row
row2 = getTableString(row2)
print("row1:")
print(row1)
print("row2:")
print(row2)

explanation = explainer_model(row1=row1, row2=row2)
print(explanation)

print("--------------------------------INTERMEDIATE--------------------------------")

single_row_res = cell_model(table1=df_row.to_string(index=False),
                   table2=getTable(target_path,0,3).to_string(index=False),
                   columns=columns)
print(single_row_res)

