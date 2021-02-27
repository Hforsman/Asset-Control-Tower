import os


def mkdir(directory: str):
    """
    Create a requested directory in the current project if that directory does not exist yet

    :param directory: Name of the
    :return: None
    """
    if os.path.exists(directory):
        print(f"Directory '{directory}' already exists, skipping mkdir")
    else:
        os.mkdir(directory)
        print(f"Created directory {directory}")


