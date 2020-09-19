def _get_python_type():
    try:
        from IPython import get_ipython
    except ImportError:
        return 'python'

    if get_ipython() is None:
        # NOTE: get_ipython() returns None when called
        # by a widget in Colab, but not in regular
        # jupyter notebooks.
        try:
            import ipykernel
        except ImportError:
            return 'python'
        if hasattr(ipykernel, 'zmqshell'):
            return 'jupyter'
        return "python"
    elif 'terminal' in get_ipython().__module__:
        return 'ipython'
    else:
        return 'jupyter'
