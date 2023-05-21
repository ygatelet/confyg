# Confyg

The Confyg package implements the `YamlConfigurableModel`, which is a flexible class for working with Pydantic models and YAML files.
It allows you to easily define and update configurations for your Python applications.

## Features

- Sub-models of a Pydantic model can be dumped to one or several YAML files for easy editing.
- The location of the YAML files and which sub-models are written to which file can be easily configured.
- When a YAML file does not exist, it is automatically created.
- When a YAML file exists, values in the file have priority over values defined in the Pydantic model. Changing the value in the Pydantic model won't change its value in the YAML file.
- If a field is added to or removed from the Pydantic model, the YAML file is automatically updated to reflect this change. 

## Usage

The package requires Python 3.10+.

```python
from pathlib import Path

from confyg import get_root, validator, BaseModel, YamlConfigurableModel
# `BaseModel` and `validator` can be imported from `confyg` instead of `pydantic`


ROOT_DIR = get_root(__file__, depth=1)  # Get the absolute path to the project's root directory
DATA_DIR = ROOT_DIR / 'data'


# Create your Pydantic models

class PathConfig(BaseModel):
    # Use absolute path to make it work from anywhere in the project
    root: Path = ROOT_DIR
    data: Path = DATA_DIR
    raw: Path = DATA_DIR / 'raw'
    processed: Path = DATA_DIR / 'processed'


class TfIdfConfig(BaseModel):
    ngram_range: list[int] = [1, 3]
    vocab_size: int = 500
    incremented: int = 1

    # Validators can be used: in this case `incremented` will be 1 in the YAML file, but 2 in the Pydantic model
    @validator('incremented', pre=True)
    def validate_incremented(cls, v):
        return v+1


class RandomForestConfig(BaseModel):
    n_estimators: int = 200
    max_depth: int = 3
    max_features: str = 'sqrt'


class ModelConfig(BaseModel):
    tfidf: TfIdfConfig = TfIdfConfig()  # Models can be nested
    random_forest: RandomForestConfig = RandomForestConfig()
    nn: str = 'RoBERTa'


class TrainingConfig(BaseModel):
    epochs: int = 10
    learning_rate: float = 0.001
    batch_size: int = 64


class DataConfig(BaseModel):
    preprocess: bool = True


# Create main configuration model which inherits from `YamlConfigurableModel`
class MyConfig(YamlConfigurableModel):
    path: PathConfig = PathConfig()  # Can't be dumped into YAML because `Path` objects are not serializable
    data: DataConfig = DataConfig()  # Will be dumped in its own YAML file
    model: ModelConfig = ModelConfig()  # Will be dumped with `training` sub-model
    training: TrainingConfig = TrainingConfig()

    # Use the `YamlConfig` inner class to specify the YAML directory
    # and which models should be dumped to which YAML files
    class YamlConfig:
        YAML_PATH = 'path/to/yaml'
        MODEL_MAPPING = {
            'data_config': ['data'],
            'ml_config': ['model', 'training'],
        }


# Initialize the model
cfg = Config()
```

Now you can access your configuration from anywhere in the project:
```python
from config import cfg

print(cfg.training.epochs)  # 10
print(cfg.model.tfidf.vocab_size)  # 500
```

If you've updated `ml_config.yaml` to contain `epochs: 20`, then the next time you create an instance of `MyConfig`, the updated value will be used:

```python
print(cfg.training.epochs)  # 20
```

If a field is added to or removed from the Pydantic model, then the next time you create an instance of `MyConfig`, the structure of the YAML will reflect this change.
