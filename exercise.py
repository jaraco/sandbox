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


def is_present(word, array, position, visited_indexes=set()):
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
    x, y = position
    return array[x][y] == letter and any(
        is_present(word[:1], array, candidate, visited_indexes.union([position]))
        for candidate in adjacent_indices(array, position) - visited_indexes
    )


def adjacent_indices(array, position):
    """
    Find indexes into array adjacent to position.

    Assumes square array
    """
    x, y = position
    width, height = len(array), len(array[0])
    return set(
        (i, j)
        for i in range(x-1, x+2)
        for j in range(y-1, y+2)
        if 0 <= i < width
        and 0 <= j < height
        and (i==x or j==y)
        and (x, y) != (i, j)
    )


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
    assert adjacent_indices(array_A, (0,0)) == set([(1,0), (0,1)])
    assert adjacent_indices(array_A, (1,1)) == set([(0,1), (1,0), (2, 1), (1, 2)])
    assert is_present_anywhere('ABCD', array_A)
    assert not is_present_anywhere('ABCE', array_A)
    assert is_present_anywhere('CGFEI', array_A)
    assert not is_present_anywhere('ABA', array_A)
    assert is_present_anywhere('BOY', array_B)
    assert is_present_anywhere('HOBO', array_B)
    assert not is_present_anywhere('BOHOB')

if __name__ == '__main__':
    test_cases()
