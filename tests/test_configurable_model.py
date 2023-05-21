from pathlib import Path

import pytest
import yaml
from pydantic import validator

from confyg import BaseModel, YamlConfigurableModel


class Model1(BaseModel):
    attribute_1a: int = 1
    attribute_1b: str = 'value'
    attribute_1c: int = 1

    @validator('attribute_1c')
    def increment(cls, v):
        return v + 1


class Model2(BaseModel):
    attribute_2a: str = 'other value'
    attribute_2b: float = 0.01


class BlockConfig(YamlConfigurableModel):
    model_1: Model1 = Model1()
    model_2: Model2 = Model2()

    class YamlConfig:
        YAML_PATH: Path = Path('/tmp')  # Test as `Path`
        MODEL_MAPPING: dict[str, list[str]] = {
            'models.yaml': ['model_1', 'model_2'],
        }


class SplitConfig(YamlConfigurableModel):
    model_1: Model1 = Model1()
    model_2: Model2 = Model2()

    class YamlConfig:
        YAML_PATH: Path = '/tmp'  # Test path as `str`
        MODEL_MAPPING: dict[str, list[str]] = {
            'model_1': ['model_1'],
            'model_2': ['model_2'],
        }


@pytest.fixture
def yaml_files(request):
    yaml_file_paths = [
        Path("/tmp/models.yaml"),
        Path("/tmp/model_1.yaml"),
        Path("/tmp/model_2.yaml"),
    ]

    def remove_files():
        for yaml_file in yaml_file_paths:
            if yaml_file.is_file():
                yaml_file.unlink()

    # Add finalizer to be called after the test function completes
    request.addfinalizer(remove_files)

    return yaml_file_paths


@pytest.fixture
def block_yaml_content():
    return '''\
    model_1:
      attribute_1a: 2
      attribute_1b: value
      attribute_1c: 41
    model_2:
      attribute_2a: new value
      attribute_2b: -0.01
    '''


@pytest.fixture
def nested_yaml_content():
    return '''\
    model_1:
      attribute_1a: 2
      attribute_1b: value
      sub_model_1a:
        attribute_1c: 41
        attribute_1d: some_value
        sub_sub_model_1a:
          attribute_1f: nested_value
          attribute_1g: 1000
      attribute_1e: 100
    model_2:
      attribute_2a: new value
      attribute_2b: -0.01
    '''


def test_yaml_creation(yaml_files):
    for yaml_file in yaml_files:
        assert not yaml_file.is_file()

    # Creating model instance should generate the YAML file
    BlockConfig()
    SplitConfig()

    for yaml_file in yaml_files:
        assert yaml_file.is_file()


def test_yaml_priority(yaml_files, block_yaml_content):
    # Create YAML
    yaml_files[0].parent.mkdir(exist_ok=True)
    yaml_files[0].touch()
    yaml_files[0].write_text(block_yaml_content)

    # Load model
    block_config = BlockConfig()
    assert block_config.model_1.attribute_1a == 2
    assert block_config.model_1.attribute_1b == 'value'
    assert block_config.model_1.attribute_1c == 42  # Test validator in sub-model
    assert block_config.model_2.attribute_2a == 'new value'
    assert block_config.model_2.attribute_2b == -0.01

    yaml_files[0].unlink()


def test_nonexistent_yaml_path():
    class MockModel(BaseModel):
        attr: int = 1

    class NonExistentPathConfig(YamlConfigurableModel):
        model_1: MockModel = MockModel()

        class YamlConfig:
            MODEL_MAPPING = {
                'model': ['model_1']
            }

    # Should raise an error if there is no path or mapping
    with pytest.raises(AttributeError):
        NonExistentPathConfig()


def test_nonexistent_model_mapping():
    class MockModel(BaseModel):
        attr: int = 1

    class NonExistentModelMappingConfig(YamlConfigurableModel):
        model_1: MockModel = MockModel()

        class YamlConfig:
            YAML_PATH = Path('/tmp')

    # Shouldn't raise an error if there is no path or mapping
    NonExistentModelMappingConfig()


def test_nested_yaml_update(yaml_files, nested_yaml_content):
    # Create YAML
    yaml_files[0].parent.mkdir(exist_ok=True)
    yaml_files[0].touch()
    yaml_files[0].write_text(nested_yaml_content)

    class SubSubModel(BaseModel):  # More nested model
        attribute_1f: str = 'other_nested_value'
        # no `attribute_1g`
        attribute_1h: str = 'new_nested_value'

    class SubModel(BaseModel):
        attribute_1c: int = 42
        sub_sub_model_1a: SubSubModel = SubSubModel()  # Changed more nested model

    class NewModel1(BaseModel):
        attribute_1a: int = 2
        attribute_1b: str = 'value'
        sub_model_1a: SubModel = SubModel()  # Changed sub-model
        # no `attribute_1e`

    class Model3(BaseModel):
        attribute_3c: bool = True

    class DifferentConfig(YamlConfigurableModel):
        model_1: NewModel1 = NewModel1()
        # no `model_2`
        model_3: Model3 = Model3()

        class YamlConfig:
            YAML_PATH = yaml_files[0].parent
            MODEL_MAPPING = {
                yaml_files[0].stem: ['model_1', 'model_3'],
            }

    DifferentConfig()

    with open(yaml_files[0]) as f:
        data = yaml.safe_load(f)

    assert 'model_1' in data.keys()
    assert 'sub_model_1a' in data['model_1'].keys()  # Sub-model still exists
    assert 'sub_sub_model_1a' in data['model_1']['sub_model_1a'].keys()  # Sub-model still exists
    assert 'model_2' not in data.keys(), data  # Model removed
    assert 'model_3' in data.keys()  # Model added
    assert 'attribute_1c' in data['model_1']['sub_model_1a'].keys()  # Attribute still exists
    assert 'attribute_1d' not in data['model_1']['sub_model_1a'].keys()  # Attribute removed
    assert 'attribute_1f' in data['model_1']['sub_model_1a']['sub_sub_model_1a'].keys()  # Attribute still exists
    assert 'attribute_1g' not in data['model_1']['sub_model_1a']['sub_sub_model_1a'].keys()  # Attribute removed
    assert 'attribute_1h' in data['model_1']['sub_model_1a']['sub_sub_model_1a'].keys()  # New attribute
    assert 'attribute_1e' not in data['model_1'].keys()  # Attribute removed from main model
