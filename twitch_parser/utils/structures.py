

def empty_list_to_none(list_or_none):
    assert list_or_none is None or isinstance(list_or_none, (list, tuple))
    return list_or_none if list_or_none else None