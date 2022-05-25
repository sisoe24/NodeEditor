import os
import sys


file, *args = sys.argv

if args:
    node_class, node_title = args
else:
    node_class = input('Node class name: ')
    node_title = input('Node title: ')


node_file = f'src/nodes/node/{node_class.lower()}.py'

if not os.path.exists(node_file):

    with open('src/template/sample_node.py', 'r+', encoding='utf-8') as file:
        content = file.read()
        content = content.replace('__NODECLASS__', node_class)
        content = content.replace('__NODETITLE__', node_title)

    with open(f'src/nodes/classes/{node_class.lower()}.py', 'w') as file:
        file.write(content)
else:
    print('File exists already.')
