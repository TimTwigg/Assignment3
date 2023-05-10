# module to index the dataset
# test on the small dataset since the large one will probably take a while to run
# actual index creation MUST be done with the large dataset since we are a CS group

from pathlib import Path

SMALL_DATASET_ROOT = "data/analyst_dataset"
LARGE_DATASET_ROOT = "data/developer_dataset"