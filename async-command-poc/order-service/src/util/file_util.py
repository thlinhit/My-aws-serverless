import json
import os


def load_json_schema(file_name: str):
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, 'resources', 'schemas', file_name)
        with open(file_path, 'r') as file:
            schema = json.load(file)
        return schema
    except FileNotFoundError:
        raise Exception(f"Schema file '{file_name}' not found in the specified directory.")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to decode JSON from '{file_name}': {str(e)}")
