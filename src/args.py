TARGET_COLUMN_THRESHOLD = 20            # it is used to decide for the algorithm used in few shot prompt preparation.
HIGH_TARGET_COLUMN_MAPPING = 30         # it is used to decide for the example count for CellModel

ROW_MODEL_FEW_SHOT_COUNT_SMALL = 6      # sets the number of few shot prompts for small tables
ROW_MODEL_PERCENTAGE_SMALL = 0.6        # sets the remaining columns percentage after randomly removing them for small tables.
ROW_MODEL_FEW_SHOT_COUNT_BIG = 3        # sets the number of few shot prompts for big tables
ROW_MODEL_PERCENTAGE_BIG = 0.8          # sets the remaining columns percentage after randomly removing them for big tables.

CELL_MODEL_EXAMPLES_COUNT_SMALL = 5     # The number of examples needed for CellModel for small tables 
CELL_MODEL_EXAMPLES_COUNT_BIG   = 3     # The number of examples needed for CellModel for big tables