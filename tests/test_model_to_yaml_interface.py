from pathlib import Path

import pytest
import yaml

from weldyn import BaseModel, YamlConfigurableModel
from weldyn.model_to_yaml_interface import load_yaml, check_yaml_path, get_model_mapping_and_path


def test_generate_yaml_from_model(tmp_path):
    class MockSubModel(BaseModel):
        attr: str = 'value'
        test: int = 2

    class MockModel(YamlConfigurableModel):
        sub_model: MockSubModel = MockSubModel()

        class YamlConfig:
            YAML_PATH = tmp_path
            MODEL_MAPPING = {
                'test': ['sub_model'],
            }

    MockModel()
    with open(tmp_path / "test.yaml") as f:
        data = yaml.safe_load(f)

    assert data == {'sub_model': {'attr': 'value', 'test': 2}}


def test_load_yaml_to_model(tmp_path):
    with open(tmp_path / "test.yaml", "w") as f:
        yaml.dump({'attr': {'attr': 42}}, f)

    data = load_yaml(tmp_path / "test.yaml")

    assert data == {'attr': {'attr': 42}}


def test_check_yaml_path(tmp_path):
    yaml_file_path = check_yaml_path("test", tmp_path)

    assert yaml_file_path == tmp_path / "test.yaml"


def test_check_model_overlap():
    class MockSubModel(BaseModel):
        attr: str = 'value'
        test: int = 2

    class MockModel(YamlConfigurableModel):
        sub_model: MockSubModel = MockSubModel()

        class YamlConfig:
            YAML_PATH = '/tmp'
            MODEL_MAPPING = {
                'model_1': ['sub_model'],
                'model_2': ['sub_model'],
            }

    with pytest.raises(ValueError):
        MockModel()


def test_get_model_mapping_and_path():
    class ExampleConfigurableModel(YamlConfigurableModel):
        class YamlConfig:
            YAML_PATH: Path = Path('/tmp')
            MODEL_MAPPING: dict[str, list[str]] = {
                'models.yaml': ['schema_1', 'schema_2'],
            }

    yaml_path, model_mapping = get_model_mapping_and_path(ExampleConfigurableModel)

    assert yaml_path == Path('/tmp')
    assert model_mapping == {'models.yaml': ['schema_1', 'schema_2']}
