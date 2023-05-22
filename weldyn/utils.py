from pathlib import Path


def get_root(file: str, depth: int = 2) -> Path:
    """
    Returns the Path object representing the root directory of the project.

    This function is typically used in configuration files to determine the absolute path of the root directory.
    Root is determined by traversing upwards from the current file's location.

    :param file: Pass `__file__` to determine the root path based on the current file's location.
    :param depth: The number of directory levels to traverse upwards from the current file to reach the root.
    :return: Path object representing the root directory of the project.
    """
    current_file = Path(file).resolve()  # Absolute path of the current file
    root_dir = current_file.parents[depth]  # Root of the project
    return root_dir
