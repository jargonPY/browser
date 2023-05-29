import tkinter.font
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union, TypeVar
from browser_html.html_parser import Node
from draw_commands import DrawCommand
from browser_layout.box_margin import Margin, resolve_margin


"""
cursor_x --> rel_x
x        --> abs_x
"""


@dataclass
class Padding:
    top: float = 0
    bottom: float = 0
    right: float = 0
    left: float = 0


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

        self.margin = resolve_margin(node)
        self.padding = Padding()

        self.font: tkinter.font.Font = tkinter.font.Font()

    @property
    def total_height(self) -> float:
        # todo this method assumes 'block_height' is only the height of the content, right now that is not the case
        # todo 'block_height' currently represents the total height of the block
        return self.block_height + self.margin.top + self.margin.bottom + self.padding.top + self.padding.bottom

    @property
    def y_bottom(self) -> float:
        return self.abs_y + (self.block_height - self.margin.top - self.padding.top)

    @abstractmethod
    def layout(self) -> None:
        pass

    @abstractmethod
    def paint(self, display_list: list[DrawCommand]) -> None:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


# * Type is used for representing class types in MyPy, while TypeVar is used for defining type variables.
T = TypeVar("T", bound=Layout)
