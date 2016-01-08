import itertools


def is_present_anywhere(word, array):
    """
    Can the word be found in the two-dimensional array
    of characters by traversing vertically or horizontally
    starting at any position.
    """
    return any(
        is_present(word, array, position=pos)
        for pos in initial_positions(array)
    )


def initial_positions(array):
    width = len(array)
    height = len(array[0])
    return itertools.product(range(width), range(height))


def is_present(word, array, position, visited_indexes=()):
    """
    Can the word be found in the two-dimensional array
    by traversing vertically or horizontally starting at
    position.
    """
    assert isinstance(word, str)
    # length of each row must be the same
    assert len(set(len(row) for row in array)) == 1
    if word == '':
        return True
    letter = word[0]
    indexes = matching_indexes(letter, array, position, visited_indexes)
    if not indexes:
        return False
    return any(
        is_present(word[:1], array, position, visited_indexes + (position,))
        for position in indexes
    )


def matching_indexes(letter, array, position, visited_indexes):
    """
    find indexes into array that match letter adjacent to position
    """
    x, y = position
    width, height = len(array), len(array[0])
    indexes = (
        (i, j)
        for i in (x - 1, x + 1)
        for j in (y - 1, y + 1)
        if letter == array[i][j]
        and 0 <= i < width
        and 0 <= j < height
        and (i,j) not in visited_indexes
    )
    return indexes


array_A = [
    'ABCD',
    'EFGH',
    'IJKL',
    'MNOP',
]

array_B = [
    'BOY',
    'OH-',
    'YOB',
]

def test_cases():
    assert is_present_anywhere('ABCD', array_A)
    assert not is_present_anywhere('ABCE', array_A)
    assert is_present_anywhere('CGFEI', array_A)
    assert not is_present_anywhere('ABA', array_A)
    assert is_present_anywhere('BOY', array_B)
    assert is_present_anywhere('HOBO', array_B)
    assert not is_present_anywhere('BOHOB')

if __name__ == '__main__':
    test_cases()
