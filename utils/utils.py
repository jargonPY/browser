from typing import TypeVar, Protocol
from browser_html.html_nodes import Node


def tree_to_list(tree, list_of_nodes):
    list_of_nodes.append(tree)
    for child in tree.children:
        tree_to_list(child, list_of_nodes)
    return list_of_nodes


def print_tree(node: Node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)


def stringify_tree(node: Node):
    text = "\n"

    def recurse(node: Node, indent=0):
        nonlocal text
        text += " " * indent + repr(node) + "\n"

        for child in node.children:
            recurse(child, indent + 2)

    recurse(node)
    return text
