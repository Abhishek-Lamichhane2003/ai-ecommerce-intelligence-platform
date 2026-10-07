from pathlib import Path

import kagglehub

from .settings import DATA_DIR, DATA_FILE


KAGGLE_DATASET = "jacksondivakarr/online-shopping-dataset"
KAGGLE_SOURCE_FILE = "file.csv"


def ensure_dataset():
    # If the dataset already exists, do nothing.
    if DATA_FILE.exists():
        return DATA_FILE

    # Create the data folder if needed.
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Download file.csv from Kaggle.
    kagglehub.dataset_download(
        KAGGLE_DATASET,
        path=KAGGLE_SOURCE_FILE,
        output_dir=str(DATA_DIR),
    )

    downloaded_file = DATA_DIR / KAGGLE_SOURCE_FILE

    if not downloaded_file.exists():
        raise FileNotFoundError(
            "Kaggle download completed, but file.csv could not be found."
        )

    # Rename file.csv to the name our project expects.
    downloaded_file.replace(DATA_FILE)

    return DATA_FILE
