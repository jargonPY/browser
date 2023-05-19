from abc import ABC, abstractmethod
from browser_html.html_nodes import Node, Element


class Selector(ABC):
    def __init__(self) -> None:
        self.priority = 1

    @abstractmethod
    def matches(self, node: Node) -> bool:
        """
        Tests whether the selector matches a specific element.
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class TagSelector(Selector):
    def __init__(self, tag: str) -> None:
        self.tag = tag
        self.priority = 10

    def matches(self, node: Node) -> bool:
        return isinstance(node, Element) and self.tag == node.tag

    def __repr__(self) -> str:
        return f"TagSelector({self.tag})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TagSelector):
            return self.tag == other.tag and self.priority == other.priority
        return False


class ClassSelector(Selector):
    def __init__(self, css_class_name: str) -> None:
        self.css_class_name = css_class_name
        self.priority = 20

    def matches(self, node: Node) -> bool:
        return (
            isinstance(node, Element) and "class" in node.attributes and self.css_class_name == node.attributes["class"]
        )

    def __repr__(self) -> str:
        return f"ClassSelector({self.css_class_name})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ClassSelector):
            return self.css_class_name == other.css_class_name and self.priority == other.priority
        return False


class IdSelector(Selector):
    def __init__(self, id_name: str) -> None:
        self.id_name = id_name
        self.priority = 30

    def matches(self, node: Node) -> bool:
        return isinstance(node, Element) and "id" in node.attributes and self.id_name == node.attributes["id"]

    def __repr__(self) -> str:
        return f"IdSelector({self.id_name})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, IdSelector):
            return self.id_name == other.id_name and self.priority == other.priority
        return False


class ListSelector(Selector):
    def __init__(self, tag_list: list[str]) -> None:
        self.tag_list = tag_list
        self.priority = 5

    def matches(self, node: Node) -> bool:
        return isinstance(node, Element) and node.tag in self.tag_list

    def __repr__(self) -> str:
        return f"ListSelector({self.tag_list})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ListSelector):
            return self.tag_list == other.tag_list and self.priority == other.priority
        return False


class DescendantSelector(Selector):
    def __init__(self, ancestor: Selector, descendant: Selector) -> None:
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority = ancestor.priority + descendant.priority

    def matches(self, node: Node) -> bool:
        if not self.descendant.matches(node):
            return False
        while node.parent:
            if self.ancestor.matches(node.parent):
                return True
            node = node.parent
        return False

    def __repr__(self) -> str:
        return f"DescendantSelector({self.ancestor} {self.descendant})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DescendantSelector):
            return (
                self.ancestor == other.ancestor
                and self.descendant == other.descendant
                and self.priority == other.priority
            )
        return False
