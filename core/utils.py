def rotate(array):
    return [list(i) for i in zip(*array[::-1])]


def flip_horize(array):
    return array[::-1]


def flip_vertic(array):
    return [i[::-1] for i in array]


def flip_diagonal(array):
    array = [row[:] for row in array]
    for i in range(3):
        for j in range(i + 1, 3):
            array[i][j], array[j][i] = array[j][i], array[i][j]
    return array


def flip_sec_diagonal(array):
    array = [row[:] for row in array]
    array[0][1], array[1][2] = array[1][2], array[0][1]
    array[0][0], array[2][2] = array[2][2], array[0][0]
    array[1][0], array[2][1] = array[2][1], array[1][0]
    return array


def tool(key):
    tools = {
        'h': flip_horize,
        'v': flip_vertic,
        'r': rotate,
        'd': flip_diagonal,
        'ds': flip_sec_diagonal
    }
    return tools[key]


def check(standard, matrix):
    full_changes = [[], ['h'], ['v'], ['d'], ['ds'], ['r'], ['r', 'r'], ['r', 'r', 'r']]
    for change in full_changes:
        if standard == normilize(change, matrix):
            return True, change
    return False, []


def normilize(changes, matrix):
    for change in changes:
        matrix = tool(change)(matrix)
    return [row[:] for row in matrix]


def main():
    pass


def search_node(tree, children, matrix):
    for child in children:
        match, changes = check(matrix, tree[child]['value'])
        if match:
            return child, changes


def get_child(key, tree, parent, middle=False):
    children_scores = [(child, tree[child][key]) for child in tree[parent]['children']]
    if not middle:
        return max(children_scores, key=lambda child: child[1])[0]
    else:
        if len(children_scores) == 1:
            return children_scores[0][0]
        sort_list = sorted(children_scores, key=lambda child: child[1], reverse=True)
        delta_top = sort_list[0][1] - sort_list[1][1]
        if delta_top > 9:
            return sort_list[0][0]
        return sort_list[1][0]


def middle_child(tree, parent):
    return get_child('anti_score', tree, parent, True)


def best_child(tree, parent):
    return get_child('score', tree, parent)


def worst_child(tree, parent):
    return get_child('anti_score', tree, parent)


def equal(a):
    return a[0] == a[1] == a[2]


def check_end(matrix):
    for row in matrix:
        if equal(row) and row[0] != 0:
            return row[0]
    for j in range(3):
        if equal([matrix[0][j], matrix[1][j], matrix[2][j]]) and matrix[0][j] != 0:
            return matrix[0][j]
    if equal([matrix[0][0], matrix[1][1], matrix[2][2]]) and matrix[0][0] != 0:
        return matrix[0][0]
    if equal([matrix[0][2], matrix[1][1], matrix[2][0]]) and matrix[0][2] != 0:
        return matrix[0][2]


if __name__ == '__main__':
    main()
