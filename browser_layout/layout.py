import tkinter.font
from abc import ABC, abstractmethod
from typing import Union, TypeVar
from browser_html.html_parser import Node
from draw_commands import DrawCommand


"""
cursor_x --> rel_x
x        --> abs_x
"""


class Layout(ABC):
    def __init__(self, node: Node, parent: "Layout", previous_sibling: Union["T", None]) -> None:
        self.node = node
        self.parent = parent
        self.previous_sibling = previous_sibling
        self.children: list["T"] = []

        self.abs_x: float = 0
        self.abs_y: float = 0
        self.block_width: float = 0
        self.block_height: float = 0

        self.font: tkinter.font.Font = tkinter.font.Font()

    @abstractmethod
    def layout(self) -> None:
        pass

    @abstractmethod
    def paint(self, display_list: list[DrawCommand]) -> None:
        pass


# * Type is used for representing class types in MyPy, while TypeVar is used for defining type variables.
T = TypeVar("T", bound=Layout)
