def is_present(word, array, visited_indexes=(), position=None):
    assert isinstance(word, str)
    if word == '':
        return True
    letter = word[0]
    indexes = matching_indexes(letter, array, visited_indexes, position)
    if not indexes:
        return False
    return any(
        is_present(word[:1], array, visited_indexes + (position,), position)
        for position in indexes
    )


def matching_indexes(letter, array, visited_indexes, position):
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
        if 0 <= i < width
        and 0 <= j < height
        and (i,j) not in visited_indexes
    )
    return indexes

