from browser_html.html_nodes import Node


def tree_to_list(tree: Node, list_of_nodes: list[Node]) -> list[Node]:
    list_of_nodes.append(tree)
    for child in tree.children:
        tree_to_list(child, list_of_nodes)
    return list_of_nodes


def print_tree(node: Node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)
