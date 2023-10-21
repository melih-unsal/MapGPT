from pathlib import Path
from utils import getExamples, getRow, dict2row, getRowDF, getTable, getTableString, prepareDFForCell
from models import RowModel, CellModel, ExplainerModel, ApplierModel
import os

root_folder = os.path.join(Path(__file__).parent.parent,"data")

source_path = os.path.join(root_folder, "table_B.csv")
source_path = "/home/melih/Desktop/personal/others/langchain/tests/unit_tests/document_loaders/test_docs/csv/test_one_col.csv"
target_path = os.path.join(root_folder, "template.csv")

examples, columns = getExamples(target_path,6,0.4)

# INITIALIZE MODELS
row_model = RowModel()
cell_model = CellModel()
explainer_model = ExplainerModel()
applier_model = ApplierModel()


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

reformatted_row_json = cell_model(table1=transformed_row,
                   table2=prepareDFForCell(getTable(target_path,0,5)),
                   columns=[columns])

for col in columns:
    print("-"*100)
    print("col:",col)
    print("transformed_row.get:",transformed_row.get(col))
    print("reformatted_row_json.get:",reformatted_row_json.get(col))
    if not transformed_row.get(col):
        reformatted_row_json[col] = {0:""}
    else:
        reformatted_row_json[col] = {0:reformatted_row_json[col]}
        
print("after reformatted_row_json:")
print(reformatted_row_json)

print("--------------------------------FINALIZER--------------------------------")

res = applier_model(
    source_json=getRowDF(source_path,0).to_dict(),
    target_json=reformatted_row_json,
    dataframe_json=getTable(source_path).to_dict()
    )

print(res)