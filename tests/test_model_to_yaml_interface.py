from pathlib import Path

import pytest
import yaml

from confyg import BaseModel, YamlConfigurableModel
from confyg.model_to_yaml_interface import generate_yaml_from_model, load_yaml, check_yaml_path, check_model_overlap, \
    get_model_mapping_and_path


def test_generate_yaml_from_model(tmp_path):
    class ExampleModel(BaseModel):
        attr: int = 42

    model_field = ExampleModel().__fields__["attr"]
    generate_yaml_from_model(model_field, ExampleModel, tmp_path / "test.yaml")

    with open(tmp_path / "test.yaml") as f:
        data = yaml.safe_load(f)

    assert data == {'attr': {'attr': 42}}


def test_load_yaml_to_model(tmp_path):
    with open(tmp_path / "test.yaml", "w") as f:
        yaml.dump({'attr': {'attr': 42}}, f)

    data = load_yaml(tmp_path / "test.yaml")

    assert data == {'attr': {'attr': 42}}


def test_check_yaml_path(tmp_path):
    yaml_file_path = check_yaml_path("test", tmp_path)

    assert yaml_file_path == tmp_path / "test.yaml"


def test_check_model_overlap():
    class MockModel(BaseModel):
        attr: int = 'value'

    model_field = MockModel().__fields__["attr"]
    with pytest.raises(ValueError):
        check_model_overlap(model_field, {'file1': ['attr'], 'file2': ['attr']})


def test_get_model_mapping_and_path():
    class ExampleConfigurableModel(YamlConfigurableModel):
        class YamlConfig:
            YAML_PATH: Path = Path('/tmp')
            MODEL_MAPPING: dict[str, list[str]] = {
                'models.yaml': ['model_1', 'model_2'],
            }

    yaml_path, model_mapping = get_model_mapping_and_path(ExampleConfigurableModel)

    assert yaml_path == Path('/tmp')
    assert model_mapping == {'models.yaml': ['model_1', 'model_2']}
