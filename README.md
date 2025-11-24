# Data Management and Analyze Codes

This project contains various Python scripts and Jupyter Notebook files for data management and analysis. It is designed to facilitate processes such as image and video labeling, dataset organization, data cleaning, and machine learning model training.

## Folders

- **notebooks/**: Jupyter Notebook files for image and video labeling, data cleaning, dataset splitting, and model training.
- **py/**: Python scripts for data processing, label editing, dataset creation, and analysis.

## Notable Files

### Notebooks
- `autolabel_to_image.ipynb`: Automatically add labels to images.
- `autolabel_to_video.ipynb`: Automatically add labels to videos.
- `train_fasterrcnn.ipynb`: Train models using Faster R-CNN.
- `train_valid_test_split_code.ipynb`: Split dataset into train, validation, and test sets.
- `delete_duplicate.ipynb`: Delete duplicate files.

### Python Scripts
- `coco2yolo_label_format.py`: Convert COCO label format to YOLO format.
- `make_dataset_with_equalized_labels_and_augmentations.py`: Create datasets with balanced labels and augmentations.
- `delete_edge_labels.py`: Remove edge labels.
- `merge_class_folders_to_create_datas.py`: Merge class folders to create datasets.

## Installation

1. Python 3.8+ must be installed.
2. To install required packages:
   ```bash
   pip install -r requirements.txt
   ```
   (Note: You may need to create the requirements.txt file yourself or manually install packages used in the notebooks.)

## Usage

- To run Jupyter Notebook files:
  ```bash
  jupyter notebook
  ```
- To run Python scripts:
  ```bash
  python py/<script_name>.py
  ```

## Contribution

To contribute, create a new branch, commit your changes, and open a pull request.

