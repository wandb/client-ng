import wandb

if wandb.TYPE_CHECKING:
    import typing as t


class SummaryRecord(object):
    '''Encodes a diff -- analogous to the SummaryRecord protobuf message'''
    update: t.Tuple["SummaryItem"]
    remove: t.Tuple["SummaryItem"]

    def __init__(self):
        self.update = tuple()
        self.remove = tuple()

    def _add_next_parent(self, parent_key):
        with_next_parent = SummaryRecord()
        with_next_parent.update = [
            item._add_next_parent(parent_key) for item in self.update
        ]
        with_next_parent.remove = [
            item._add_next_parent(parent_key) for item in self.remove
        ]

        return with_next_parent


class SummaryItem:
    '''Analogous to the SummaryItem protobuf message.'''
    key: t.Tuple[str]
    value: t.Any

    def __init__(self):
        self.key = tuple()
        self.value = None

    def _add_next_parent(self, parent_key):
        with_next_parent = SummaryItem()

        key = self.key
        if not isinstance(key, tuple):
            key = (key,)

        with_next_parent.key = (parent_key,) + self.key
        with_next_parent.value = self.value

        return with_next_parent
