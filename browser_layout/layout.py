from typing import Tuple, Literal, Union, Any, Type, TypeVar
import tkinter.font
from utils.constants import BLOCK_ELEMENTS
from browser_html.html_parser import Node, Element, Text
from draw_commands import DrawCommand, DrawText, DrawRect
from utils.type_hints import *

from abc import ABC, abstractmethod

# * Type is used for representing class types in MyPy, while TypeVar is used for defining type variables.
# T = TypeVar("T", bound=LayoutClass)
# T = TypeVar("T", bound="LayoutClass")


class LayoutClass(ABC):
    def __init__(self, node: Node, parent: "LayoutClass", previous_sibling: Union["T", None]) -> None:
        self.node = node
        self.parent = parent
        self.previous_sibling = previous_sibling
        # todo rework the typing here
        self.children: list[Any] = []

        self.abs_x: float = 0
        self.abs_y: float = 0

        self.block_width: float = 0
        self.block_height: float = 0

    @abstractmethod
    def layout(self) -> None:
        pass

    @abstractmethod
    def paint(self, display_list: list[DrawCommand]) -> None:
        pass


T = TypeVar("T", bound=LayoutClass)


"""
cursor_x --> rel_x
x        --> abs_x
"""

FONTS = {}


def get_font(size, weight, slant):
    key = (size, weight, slant)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=slant)
        FONTS[key] = font
    return FONTS[key]


class LineLayout(LayoutClass):
    def __init__(self, node: Node, parent: "LayoutClass", previous_sibling: Union["LineLayout", None]) -> None:
        super().__init__(node, parent, previous_sibling)
        # self.node = node
        # self.parent = parent
        # self.previous_sibling = previous_sibling
        self.children: list["TextLayout"] = []

        # self.abs_x: float = 0
        # self.abs_y: float = 0

        # self.block_width: float = 0
        # self.block_height: float = 0

    def layout(self) -> None:
        """
        Lines stack vertically and take up their parent’s full width, so computing abs_x, abs_y
        and block_width is the same as for the other boxes.
        """
        self.block_width = self.parent.block_width
        self.abs_x = self.parent.abs_x

        if self.previous_sibling is not None:
            self.abs_y = self.previous_sibling.abs_y + self.previous_sibling.block_height
        else:
            self.abs_y = self.parent.abs_y

        # Before computing block_height, lay out each word
        for word in self.children:
            word.layout()

        """
        Note that this code is reading from a font field on each word and writing to each word’s y field.
        That means that inside TextLayout’s layout method, we need to compute x, width, and height, but
        also font, and not y. Remember that for later.
        """
        max_ascent = max([word.font.metrics("ascent") for word in self.children])
        baseline = self.abs_y + 1.25 * max_ascent
        for word in self.children:
            word.abs_y = baseline - word.font.metrics("ascent")
        max_descent = max([word.font.metrics("descent") for word in self.children])

        self.block_height = 1.25 * (max_ascent + max_descent)

    def paint(self, display_list: list[DrawCommand]) -> None:
        for child in self.children:
            child.paint(display_list)


class TextLayout(LayoutClass):
    def __init__(
        self, node: Node, parent: "LayoutClass", previous_sibling: Union["TextLayout", None], word: str
    ) -> None:
        super().__init__(node, parent, previous_sibling)
        # self.node = node
        # self.parent = parent
        # self.previous_sibling = previous_sibling
        self.children: list["LayoutClass"] = []
        self.word = word
        self.font: tkinter.font.Font = tkinter.font.Font()

        # self.abs_x: float = 0
        # self.abs_y: float = 0

        # self.block_width: float = 0
        # self.block_height: float = 0

    def layout(self) -> None:
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(float(self.node.style["font-size"][:-2]) * 0.75)
        self.font = get_font(size, weight, style)

        # Do not set self.abs_y!
        self.block_width = self.font.measure(self.word)

        if self.previous_sibling is not None:
            space = self.previous_sibling.font.measure(" ")
            self.abs_x = self.previous_sibling.abs_x + space + self.previous_sibling.block_width
        else:
            self.abs_x = self.parent.abs_x

        self.block_height = self.font.metrics("linespace")

    def paint(self, display_list: list[DrawCommand]) -> None:
        color = self.node.style["color"]
        display_list.append(DrawText(self.abs_x, self.abs_y, self.word, self.font, color))


class Layout(LayoutClass):
    WIDTH, HEIGHT = 800, 600
    H_STEP, V_STEP = 13, 18

    def __init__(self, node: Node, parent: "Layout", previous_sibling: Union["Layout", None]) -> None:
        super().__init__(node, parent, previous_sibling)
        # self.node = node
        # self.parent = parent
        # self.previous_sibling = previous_sibling
        self.children: list["LayoutClass"] = []

        self.previous_word: "TextLayout" | None = None

        # self.abs_x: float = 0
        # self.abs_y: float = 0
        self.rel_x: float = 0  # offset from abs_x within the block
        self.rel_y: float = 0  # offset from abs_y within the block
        # self.block_width: float = 0
        # self.block_height: float = 0

    def layout_mode(self, html_node: Node):
        """
        This method is used to determine which layout approach to use.

        1. For leaf blocks that contain text, lay out text horizontally (use recurse and flush).
        2. For intermediate BlockLayouts with BlockLayout children, stack their children vertically (using layout_intermediate).
        """
        if isinstance(html_node, Text):
            return "inline"
        elif html_node.children:
            # ? What are the consequences of using 'block' mode for the situation described below?
            """
            There is one tricky case, where a node contains both block children like a <p> element but also text children like a
            text node or a <b> element, in such a case 'block' mode is used, but it’s probably best to think of this as a
            kind of error on the part of the web developer.
            """
            # Ex. <div> <p> Hello </p> </div>
            if any([isinstance(child, Element) and child.tag in BLOCK_ELEMENTS for child in html_node.children]):
                return "block"
            # Ex. <div> <big> Hello </big> </div>
            else:
                return "inline"
        else:
            return "block"

    def compute_block_width(self):
        # Blocks are as wide as their parents
        self.block_width = self.parent.block_width

    def compute_block_x_position(self):
        # The block starts at its parent's left edge
        self.abs_x = self.parent.abs_x

    def compute_block_y_position(self):
        # Vertical position depends on the position and height of their previous sibling
        if self.previous_sibling:
            self.abs_y = self.previous_sibling.abs_y + self.previous_sibling.block_height
        # If there is no previous siblng, the block starts at the paren'ts top edge
        else:
            self.abs_y = self.parent.abs_y

    # def compute_block_height(self, mode: Literal["block", "inline"]):
    #     #  A block that contains other blocks should be tall enough to contain all of its children, so its height should be the sum of its children’s heights
    #     if mode == "block":
    #         self.block_height = sum([child.block_height for child in self.children])
    #     # A block that contains text doesn’t have children; instead, it needs to be tall enough to contain all its text
    #     else:
    #         self.block_height = self.rel_y

    def compute_block_height(self) -> None:
        """
        Compute the height of a paragraph of text by summing the height of its lines, so this part of the code
        no longer needs to be different depending on the layout mode.
        """
        self.block_height = sum([child.block_height for child in self.children])

    def layout(self):
        """
        Layout steps:
        1. Compute the 'width', 'abs_x', and 'abs_y' fields from the 'parent' and 'previous_sibling' fields.
        2. Create layout object for each child element.
        3. Layout the children nodes by calling their layout method recursively.
        4. Compute the 'height' field based on the child node heights.
        """
        self.compute_block_width()
        self.compute_block_x_position()
        self.compute_block_y_position()

        mode = self.layout_mode(self.node)
        if mode == "block":
            self.layout_intermediate_block()
        else:
            self.new_line()
            self.layout_leaf_block(self.node)

            # self.layout_leaf_block(self.node)
            # # As usual with buffers, need to make sure the buffer is flushed once all tokens are processed
            # self.flush()

        for child in self.children:
            child.layout()

        self.compute_block_height()

    def layout_intermediate_block(self):
        previous = None
        for child in self.node.children:
            # Constructs a Layout from an Element node, using the previous child as the sibling argument
            next = Layout(child, self, previous)
            # Append the child Layout object to this (parent) array of children
            self.children.append(next)
            # Store the child ot be used as the previous sibling
            previous = next

    def layout_leaf_block(self, node: Node):
        if isinstance(node, Text):
            self.text(node)
        elif isinstance(node, Element):
            if node.tag == "br":
                self.new_line()

            for child in node.children:
                self.layout_leaf_block(child)

    def get_font(self, node: Node):
        weight = node.style["font-weight"]
        style = node.style["font-style"]

        # Convert CSS "normal" to Tk "roman"
        if style == "normal":
            style = "roman"
        # Convert CSS pixels to Tk points
        size = int(float(node.style["font-size"][:-2]) * 0.75)
        return get_font(size, weight, style)

    def text(self, node: Text) -> None:
        for word in node.text.split():
            font = self.get_font(node)
            word_width = font.measure(word)

            # Move to new line
            if self.rel_x + word_width > self.block_width:
                self.new_line()

            # The LineLayouts are children of the BlockLayout, so the current line can be found at the end of the children array
            line = self.children[-1]
            text = TextLayout(node, line, self.previous_word, word)
            line.children.append(text)
            self.previous_word = text

            self.rel_x += word_width + font.measure(" ")

    def new_line(self) -> None:
        self.previous_word = None
        self.rel_x = 0
        last_line = self.children[-1] if self.children else None

        # todo replace assertion with a different type checking mechanism
        assert (
            isinstance(last_line, LineLayout) or last_line is None
        ), f"Expected 'last_line' to be of type 'LineLayout' or 'None', received {type(last_line)} instead"

        new_line = LineLayout(self.node, self, last_line)
        self.children.append(new_line)

    def paint(self, display_list: list[DrawCommand]):
        """
        This method collect all the draw commands into the 'display_list'.

        Then 'Browser.draw()' can sequentially iterate over the commands and draw each command
        to the screen.
        """

        if isinstance(self.node, Element):
            bg_color = self.node.style.get("background-color", "transparent")
            if bg_color != "transparent":
                x2, y2 = self.abs_x + self.block_width, self.abs_y + self.block_height
                rect = DrawRect(self.abs_x, self.abs_y, x2, y2, bg_color)
                display_list.append(rect)

        for child in self.children:
            child.paint(display_list)


class DocumentLayout:
    def __init__(self, node: Node) -> None:
        self.node = node
        self.parent = None
        self.children: list[Layout] = []

    def layout(self):
        child = Layout(self.node, self, None)
        self.children.append(child)

        self.block_width = Layout.WIDTH - 2 * Layout.H_STEP
        self.abs_x = Layout.H_STEP
        self.abs_y = Layout.V_STEP
        child.layout()
        self.block_height = child.block_width + 2 * Layout.V_STEP

    def paint(self, display_list: list[DrawCommand]):
        self.children[0].paint(display_list)
