def _get_python_type():
    try:
        # NOTE: Special casing colab because
        # get_ipython() returns None when called
        # by a widget in Colab, but not in regular
        # jupyter notebooks.
        import google.colab  # noqa: F401
        return 'jupyter'
    except ImportError:
        pass
    try:
        from IPython import get_ipython
    except ImportError:
        return 'python'
    if get_ipython() is None:
        return "python"
    elif 'terminal' in get_ipython().__module__:
        return 'ipython'
    else:
        return 'jupyter'
