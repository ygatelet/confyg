from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class OrderedDumper(yaml.Dumper):
    """
    A YAML Dumper that preserves the order of the Pydantic model's fields.
    """
    pass


yaml.add_representer(
    dict,  # Use dict to preserve order when dumping the YAML
    lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items()),
    Dumper=OrderedDumper
)


def load_yaml(file_path: Path) -> dict[str, Any]:
    """
    Load an existing YAML file.

    :param file_path: Path of the associated YAML file (must contain the file name and extension)
    :return: Dictionary of the loaded YAML file
    """
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def dump_yaml_data(yaml_file_path: Path, data: dict[str, Any]) -> None:
    """
    Dump data into a YAML file at a given file path.

    :param yaml_file_path: Path to the YAML file to dump into.
    :param data: Dictionary to dump into the YAML file.
    """
    with open(yaml_file_path, 'w') as file:
        yaml.dump(data, file, Dumper=OrderedDumper)


def generate_yaml_from_model(field: Field, model_class: type[BaseModel], yaml_file_path: Path) -> None:
    """
    Generates a YAML file representing a given Pydantic model.

    This function serializes a new instance of the provided Pydantic model class, using the model's default values.
    The serialized model is then written to a new YAML file at the specified path.

    :param field: The Pydantic field being processed.
    :param model_class: The class of the Pydantic field being processed.
    :param yaml_file_path: The desired Path for the new YAML file. This path must include the desired file name and
    extension.
    """
    model_data = model_class().dict()
    data = {field.name: model_data}
    dump_yaml_data(yaml_file_path, data)


def update_nested_yaml_from_model(model_data: dict[str, Any], yaml_data: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively update the YAML data based on the given model data.

    :param model_data: Data generated from the Pydantic model, to update the YAML data.
    :param yaml_data: Original YAML data to be updated.
    :return: Updated YAML data after merging with the model data.
    """
    updated_data = {}

    for key, value in model_data.items():
        # If this key is in the YAML data and is a dictionary, go one level deeper
        if key in yaml_data and isinstance(value, dict) and isinstance(yaml_data[key], dict):
            updated_data[key] = update_nested_yaml_from_model(value, yaml_data[key])
        # If the key is in the YAML data but the structure changed, take model's structure but YAML's value
        elif key in yaml_data and not isinstance(value, dict):
            updated_data[key] = yaml_data[key]
        # If the key is not in the YAML data, take the model's data
        else:
            updated_data[key] = value
    return updated_data


def remove_missing_sections(data: dict[str, Any], models: list[str]) -> dict[str, Any]:
    """
    Remove missing sections from the given data dictionary.

    :param data: Original data dictionary.
    :param models: List of models that are expected to be present in the data.
    :return: Updated dictionary after removing missing sections.
    """
    missing_sections = [section for section in data if section not in models]
    for section in missing_sections:
        del data[section]
    return data


def update_yaml_from_model(field: Field, model_class: type[BaseModel], models: list[str], yaml_file_path: Path):
    """
    Update a YAML file based on a given Pydantic model and field.

    :param field: Pydantic field to be processed.
    :param model_class: Class of the Pydantic field to be processed.
    :param models: List of models that are expected to be present in the YAML file.
    :param yaml_file_path: Path to the existing YAML file.
    :return: Data of the Pydantic field as present in the YAML file, either pre-existing or newly generated.
    """
    data = load_yaml(yaml_file_path)

    model_data = model_class().dict()

    if field.name not in data or any(key not in data[field.name] for key in model_data):
        data[field.name] = model_data

    if field.name in data and isinstance(data[field.name], dict):
        data[field.name] = update_nested_yaml_from_model(model_data, data[field.name])

    data = remove_missing_sections(data, models)
    dump_yaml_data(yaml_file_path, data)

    return data[field.name]


def check_yaml_path(yaml_file: str, yaml_path: Path) -> Path:
    """
    Check if the YAML file exists and create it if it doesn't.
    """
    if not yaml_file.endswith('.yaml') and not yaml_file.endswith('.yml'):
        yaml_file += '.yaml'
    yaml_file_path = yaml_path / yaml_file
    yaml_file_path.parent.mkdir(exist_ok=True, parents=True)
    return yaml_file_path


def check_model_overlap(field: Field, model_mapping: dict[str, list[str]]) -> None:
    """
    Check if a sub-model is dumped in several files.
    """
    if len([yaml_file for yaml_file, models in model_mapping.items() if field.name in models]) > 1:
        raise ValueError(f"The sub-model {field.name} cannot be dumped in more than one YAML file.")


def get_model_mapping_and_path(cls) -> tuple[Path, dict[str | None, list[str]]]:
    """
    Parse inner `YamlConfig` class to get YAML path and model mapping.
    """
    """
    Extracts the YAML path and model mapping from a Pydantic model's YamlConfig.

    This function inspects the YamlConfig of a Pydantic model class and returns the YAML path and model mapping, if
    defined. If not defined, it returns suitable defaults.

    :param cls: The Pydantic model class.
    :return: A tuple containing the YAML path and model mapping.
    """
    yaml_path = cls.YamlConfig.YAML_PATH
    if hasattr(cls.YamlConfig, "MODEL_MAPPING"):
        model_mapping = cls.YamlConfig.MODEL_MAPPING
    else:
        model_mapping = {}
    return yaml_path, model_mapping
