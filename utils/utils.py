from typing import TypeVar, Protocol
from browser_html.html_nodes import Node


class Tree(Protocol):
    children: list["Tree"]


T = TypeVar("T", bound="Tree")


def tree_to_list(tree: Tree, list_of_nodes: list[Tree]) -> list[Tree]:
    list_of_nodes.append(tree)
    for child in tree.children:
        tree_to_list(child, list_of_nodes)
    return list_of_nodes


def print_tree(node: Node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)
