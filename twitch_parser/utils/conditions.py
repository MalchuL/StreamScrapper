

# TODO cover by tests
def parse_condition(condition: str, default_condition='==', to_type=float):
    if '<=' in condition:
        def less_or_equal(a, b):
            return a <= b

        return less_or_equal, to_type(condition[2:])
    elif '>=' in condition:
        def greater_or_equal(a, b):
            return a >= b

        return greater_or_equal, to_type(condition[2:])
    elif '==' in condition:
        def equal(a, b):
            return a == b

        return equal, to_type(condition[2:])
    elif '!=' in condition or '<>' in condition:
        def not_equal(a, b):
            return a != b

        return not_equal, to_type(condition[2:])
    elif '=' in condition:
        def equal(a, b):
            return a == b

        return equal, to_type(condition[1:])
    elif '<' in condition:
        def less(a, b):
            return a < b

        return less, to_type(condition[1:])
    elif '>' in condition:
        def greater(a, b):
            return a > b

        return greater, to_type(condition[1:])
    else:
        return parse_condition(default_condition + condition)


class KeyValueComparator:
    def __init__(self, kv_conditions):
        self.conditions = {}
        if kv_conditions is not None and len(kv_conditions):
            for key, condition in kv_conditions.items():
                self.conditions[key] = parse_condition(condition)

    def __call__(self, data):
        return self.check_condition(data)

    def check_condition(self, data: dict):
        for k, (comparator, value) in self.conditions.items():
            if not comparator(data[k], value):
                return False
        return True