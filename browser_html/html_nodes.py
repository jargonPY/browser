from typing import TYPE_CHECKING
from abc import ABC
from typing import Dict, Union

if TYPE_CHECKING:
    from utils.type_hints import CSSProperties


class Node(ABC):
    def __init__(self, parent: Union["Node", None]) -> None:
        self.parent = parent
        self.children: list[Node] = []
        self.style: "CSSProperties" = {}  # Added by the CSS parser


class Text(Node):
    def __init__(self, text: str, parent: Node | None) -> None:
        self.text = text
        # todo conver to 'super(parent)' call to initialize 'parent' and 'children' and 'style
        self.parent = parent
        # Even though 'Text' nodes never have children, this is added for consistency, to avoid 'isinstance' calls throughout the code
        self.children: list[Node] = []
        self.style: "CSSProperties" = {}

    def __repr__(self) -> str:
        return repr(self.text)


class Element(Node):
    def __init__(self, tag: str, attributes: Dict[str, str], parent: Node | None) -> None:
        self.tag = tag
        self.attributes = attributes
        self.parent = parent
        self.children: list[Node] = []
        self.style: "CSSProperties" = {}
        self.css_class_name = ""

    def __repr__(self) -> str:
        return f"< {self.tag} >"
