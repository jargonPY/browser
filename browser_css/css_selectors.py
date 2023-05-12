from abc import ABC, abstractmethod
from browser_html.html_nodes import Node, Element


class Selector(ABC):
    def __init__(self) -> None:
        self.prioroty = 1

    @abstractmethod
    def matches(self, node: Node) -> bool:
        pass


class TagSelector(Selector):
    def __init__(self, tag: str) -> None:
        self.tag = tag
        self.prioroty = 1

    def matches(self, node: Node) -> bool:
        """
        Tests whether the selector matches a specific element.
        """
        return isinstance(node, Element) and self.tag == node.tag


class DescendantSelector(Selector):
    def __init__(self, ancestor: Selector, descendant: Selector) -> None:
        self.ancestor = ancestor
        self.descendant = descendant
        self.prioroty = ancestor.prioroty + descendant.prioroty

    def matches(self, node: Node) -> bool:
        if not self.descendant.matches(node):
            return False
        while node.parent:
            if self.ancestor.matches(node.parent):
                return True
            node.parent
        return False
