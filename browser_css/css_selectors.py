from abc import ABC, abstractmethod
from browser_html.html_nodes import Node, Element


class Selector(ABC):
    def __init__(self) -> None:
        self.prioroty = 1

    @abstractmethod
    def matches(self, node: Node) -> bool:
        pass

    @abstractmethod
    def __repr__(self) -> str:
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

    def __repr__(self) -> str:
        return f"TagSelector({self.tag})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TagSelector):
            return self.tag == other.tag and self.prioroty == other.prioroty
        return False


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

    def __repr__(self) -> str:
        return repr(self.ancestor)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DescendantSelector):
            return (
                self.ancestor == other.ancestor
                and self.descendant == other.descendant
                and self.prioroty == other.prioroty
            )
        return False
