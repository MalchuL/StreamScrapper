

def numpad_alignment_to_moviepy(alignment):
    if alignment == 0:
        return None
    horizontal_position = None
    vertical_position = None

    if alignment in [1,4,7]:
        horizontal_position = 'left'
    elif alignment in [2,5,8]:
        horizontal_position = 'center'
    elif alignment in [3,6,9]:
        horizontal_position = 'right'
    else:
        raise ValueError(f'alignment not in [1..9] range')

    if alignment in [7,8,9]:
        vertical_position = 'top'
    elif alignment in [4,5,6]:
        vertical_position = 'center'
    elif alignment in [1,2,3]:
        vertical_position = 'bottom'
    else:
        raise ValueError(f'alignment not in [1..9] range')

    assert horizontal_position is not None
    assert vertical_position is not None
    return (horizontal_position, vertical_position)