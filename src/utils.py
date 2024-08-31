import os
import json
import yaml
import shutil
import logging

def ensure_dir(file_path):
    try:
        if not os.path.exists(file_path):
            os.makedirs(file_path)
    except Exception as e:
        logging.error(f"Error ensuring directory: {e}", exc_info=True)

def get_file_extension(file_name):
    return os.path.splitext(file_name)[-1].lower()

def save_json(data, file_path):
    try:
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file)
    except Exception as e:
        logging.error(f"Error saving JSON: {e}", exc_info=True)

def load_json(file_path):
    try:
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    except Exception as e:
        logging.error(f"Error loading JSON: {e}", exc_info=True)

def save_yaml(data, file_path):
    try:
        with open(file_path, 'w') as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False)
    except Exception as e:
        logging.error(f"Error saving YAML: {e}", exc_info=True)

def load_yaml(file_path):
    try:
        with open(file_path, 'r') as yaml_file:
            return yaml.load(yaml_file, Loader=yaml.FullLoader)
    except Exception as e:
        logging.error(f"Error loading YAML: {e}", exc_info=True)

def list_files_in_directory(directory, extensions=None):
    try:
        if extensions is None:
            return [os.path.join(directory, f) for f in os.listdir(directory)]
        else:
            return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.splitext(f)[-1].lower() in extensions]
    except Exception as e:
        logging.error(f"Error listing files in directory: {e}", exc_info=True)
        return []

def copy_files(src_directory, dest_directory, extensions=None):
    try:
        ensure_dir(dest_directory)
        files = list_files_in_directory(src_directory, extensions)
        for file in files:
            shutil.copy(file, dest_directory)
    except Exception as e:
        logging.error(f"Error copying files: {e}", exc_info=True)
