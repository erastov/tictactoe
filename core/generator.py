from .utils import check
import sqlite3

SCORES = {
    'l': 0,
    'd': 100,
    'w': 100,
}


def has_same_child(children, new_child):
    for key, child in children.items():
        match, _ = check(child['value'], new_child)
        if match:
            return True
    return False


def has_same_node(tree, new_child):
    for key, child in tree.items():
        if child['value'] == new_child:
            return key
    return False


def is_leaf(matrix):
    results = {1: 'w', 2: 'l'}
    for i in range(3):
        if matrix[i][0] == matrix[i][1] == matrix[i][2] != 0:
            return results[matrix[i][0]]
        if matrix[0][i] == matrix[1][i] == matrix[2][i] != 0:
            return results[matrix[0][i]]

    if matrix[0][0] == matrix[1][1] == matrix[2][2] != 0:
        return results[matrix[0][0]]
    if matrix[2][0] == matrix[1][1] == matrix[0][2] != 0:
        return results[matrix[2][0]]

    for i in range(3):
        for j in range(3):
            if matrix[i][j] == 0:
                return False
    return 'd'


def generate_children(id_node, tree, gamer, max_id):
    node = tree[id_node]
    matrix = node['value']
    children = {}
    next_id = max_id + 1
    for i in range(3):
        for j in range(3):
            if matrix[i][j] == 0:
                child = [row[:] for row in matrix]
                child[i][j] = gamer
                key = has_same_node(tree, child)
                if key:
                    tree[key]['parent'].add(id_node)
                    children[key] = tree[key]
                elif not has_same_child(children, child):
                    children[next_id] = {'value': child, 'parent': {id_node}}
                    next_id += 1
    return children


def get_tree():

    def result(node_id):
        node = tree[node_id]
        if node.get('result', None):
            return node['result']
        res = {'w': 0, 'd': 0, 'l': 0}
        for child_id in node['children']:
            child_res = result(child_id)
            res['w'] += child_res['w']
            res['l'] += child_res['l']
            res['d'] += child_res['d']
        return res

    def recursive(id_node, children, gamer):
        nonlocal tree
        tree[id_node]['children'] = [ide for ide, _ in children.items()]
        tree.update(children)
        gamer = 1 if gamer == 2 else 2
        for id_node, node in children.items():
            result = is_leaf(node['value'])
            if result is not False:
                tree[id_node]['result'] = {'w': 0, 'd': 0, 'l': 0}
                tree[id_node]['result'][result] = 1
                tree[id_node]['score'] = SCORES[result]
                tree[id_node]['children'] = []
            else:
                children = generate_children(id_node, tree, gamer, max(tree))
                recursive(id_node, children, gamer)

    node = {
        'value': [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ],
        'parent': None
    }
    tree = {0: node}
    gamer = 1
    children = generate_children(0, tree, gamer, 0)
    recursive(0, children, gamer)
    for k, node in tree.items():
        node['result'] = result(k)
        s = sum(node['result'].values())
        wins = node['result']['w']
        draws = node['result']['d']
        looses = node['result']['l']
        node['score'] = int((wins + draws)/s * 100)
        node['anti_score'] = int((looses + draws)/s * 100)
    return tree


def insert_db(tree):
    conn = sqlite3.connect('sqlite.db')
    c = conn.cursor()
    sql = 'INSERT INTO tree (id,value,children,parent, result, score, anti_score) VALUES (?, ?, ?, ?, ?, ?, ?)'
    for ide, node in tree.items():
        value = ','.join([' '.join([str(i) for i in row]) for row in node['value']])
        children = ' '.join([str(i) for i in node['children']])
        parent = 'NULL' if node['parent'] is None else ' '.join([str(i) for i in node['parent']])
        result = ','.join(['{}:{}'.format(k, v) for k, v in node['result'].items()])
        score = node['score']
        anti_score = node['anti_score']
        c.execute(sql, [ide, value, children, parent, result, score, anti_score])
        conn.commit()
    conn.close()


def _parser(result):
    tree = {}
    for row in result:
        tree[int(row[0])] = {
            'value': [[int(i) for i in r.split(' ')] for r in row[1].split(',')],
            'parent': [int(i) for i in row[5].split(' ')] if row[5] != 'NULL' else None,
            'children': [int(i) for i in row[2].split(' ')] if row[2] != '' else [],
            'score': int(row[4]),
            'anti_score': int(row[6]),
        }
    return tree


def get_tree_db():
    conn = sqlite3.connect('/Users/f.erastov/PycharmProjects/YTCF/sqlite.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tree')
    result = c.fetchall()
    conn.close()
    return _parser(result)


def main():
    tree = get_tree()
    insert_db(tree)


if __name__ == '__main__':
    main()
