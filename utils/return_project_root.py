from pathlib import Path


def get_project_root() -> str:
    """
    This fx is super important!
    Literally everything acts up if this isn't good.
    """
    path = str(Path(__file__).parent.parent)
    path = path.replace("\\", '/')
    return fr'{path}'


if __name__ == "__main__":
    print(get_project_root())