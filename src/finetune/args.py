import os

DATA_ROOT = "data/fine_tuning/"

COLUMN_MAPPING_ROOT = os.path.join(DATA_ROOT,"new_column_data")
ORIGINAL_DATA_ROOT = os.path.join(DATA_ROOT,"new_source_target_data")
TARGET_ROOT = os.path.join(DATA_ROOT,"new_source_target_data_result")

TARGET_ROW_PER_SOURCE_ROW = 3   # For each source row, this number of target rows will be shown to the model
DELETE_PERCENTAGE_LIMIT = 0.3   # For each row pair, some percetange of source columns will be deleted.
DELETE_PROB = 0.1 # Deleting column probablity
SHUFFLE_COLUMNS_PROB = 0.05
EXAMPLE_PER_ROW = 1

SYSTEM_MESSAGE = """You are a helper assistant that can transform Source JSON by looking at the Examples"""