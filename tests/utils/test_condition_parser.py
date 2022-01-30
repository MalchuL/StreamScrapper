import pytest

from twitch_parser.utils.conditions import parse_condition



def test_condition_number_parser():
    operations = ['', '<', '>', '=', '==', '<=', '>=', '!=', '<>']
    ints = [i for i in range(-100, 101)]
    offsets = [-1, -100, -1000, 0, +1, +100, +1000]
    # left calculated as some int + offset, ex. -100 + (-1) for first value it must be False for condition -100==-101
              #-1      -100   -1000  0     +1     +100   +1000
    targets = [[False, False, False, True,  False, False, False], # for '' must be equal
               [True,  True,  True,  False, False, False, False], # for <
               [False, False, False, False, True,  True,  True], # for >
               [False, False, False, True,  False, False, False], # for =
               [False, False, False, True,  False, False, False], # for ==
               [True,  True,  True,  True,  False, False, False],  # for <=
               [False, False, False, True,  True,  True,  True],  # for >=
               [True,  True,  True,  False, True,  True,  True],  # for !=
               [True, True, True, False, True, True, True],  # for <>
               ]

    for id_op, operation in enumerate(operations):
        for id_offset, offset in enumerate(offsets):
            for right_value in ints:

                left_value = right_value + offset
                condition = operation + str(right_value)

                condition_func, parsed_value = parse_condition(condition, to_type=int)
                target = targets[id_op][id_offset]
                assert parsed_value == right_value
                assert condition_func(left_value, right_value) == target, f'{right_value}{condition} must be {target}'

