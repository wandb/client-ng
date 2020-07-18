import os


def subdict(d, expected_dict):
    """Return a new dict with only the items from `d` whose keys occur in `expected_dict`.
    """
    return {k: v for k, v in d.items() if k in expected_dict}


def fixture_open(path):
    """Returns an opened fixture file"""
    return open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "fixtures", path))


def notebook_path(path):
    """Returns the path to a notebook"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "notebooks", path)
