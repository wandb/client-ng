import abc

import six

try:
    from typing import Callable, Optional, Tuple
except ImportError:
    pass


def _get_dict(d):
    if isinstance(d, dict):
        return d
    # assume argparse Namespace
    return vars(d)


@six.add_metaclass(abc.ABCMeta)
class SummaryDict(object):
    """dict-like which wraps all nested dictionraries in a SummarySubDict,
     and triggers self._root._callback on property changes."""

    def __init__(self):
        object.__setattr__(self, "_items", dict())
        object.__setattr__(self, "_root", None)
        object.__setattr__(self, "_parent_path", None)

    @abc.abstractmethod
    def _get_full_path(self, key=None):
        raise NotImplementedError

    def keys(self):
        return [k for k in self._items.keys() if k != "_wandb"]

    def _as_dict(self):
        return self._items

    def __getitem__(self, key):
        item = self._items[key]

        if isinstance(item, dict):
            # this nested dict needs to be wrapped:
            wrapped_item = SummarySubDict()
            object.__setattr__(wrapped_item, "_items", item)
            object.__setattr__(wrapped_item, "_parent_path", self._get_full_path(key))
            object.__setattr__(wrapped_item, "_root", self._root)

            return wrapped_item

        # this item isn't a nested dict
        return item

    def __setitem__(self, key, val):
        self._items[key] = val
        full_path = self._get_full_path(key)
        self._notify(key=full_path, val=val, data=self._root._items)

    __setattr__ = __setitem__

    def __getattr__(self, key):
        return self.__getitem__(key)

    def _notify(self, key=None, val=None, data=None):
        if not self._root._callback:
            return

        if isinstance(key, tuple) and len(key) == 1:
            callback_key = key[0]
        else:
            callback_key = key

        self._root._callback(key=callback_key, val=val, data=data)

    def update(self, d):
        self._items.update(_get_dict(d))
        full_path = self._get_full_path()
        self._notify(key=full_path, data=dict(self))

    def setdefaults(self, d):
        d = _get_dict(d)
        for k, v in six.iteritems(d):
            self._items.setdefault(k, v)
        full_path = self._get_full_path()
        self._notify(key=full_path, data=dict(self))


class Summary(SummaryDict):
    """Root node of the summary data structure. Contains the callback."""

    def __init__(self):
        super(Summary, self).__init__()
        object.__setattr__(self, "_root", self)
        object.__setattr__(self, "_callback", None)

    def _set_callback(self, cb):
        object.__setattr__(self, "_callback", cb)

    def _get_full_path(self, key=None):
        return (key,) if key else None


class SummarySubDict(SummaryDict):
    """Non-root node of the summary data structure. Contains a path to itself
    from the root."""

    def _get_full_path(self, key=None):
        return (self._parent_path + (key,)) if key else self._parent_path
