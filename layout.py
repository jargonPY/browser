from typing import Tuple, Literal
import tkinter.font
from utils.constants import BLOCK_ELEMENTS
from browser_html.html_parser import Node, Element, Text
from draw_commands import DrawCommand, DrawText, DrawRect
from utils.type_hints import *

FONTS = {}


def get_font(size, weight, slant):
    key = (size, weight, slant)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=slant)
        FONTS[key] = font
    return FONTS[key]


class Layout:
    WIDTH, HEIGHT = 800, 600
    H_STEP, V_STEP = 13, 18

    def __init__(self, node: Node, parent: "Layout", previous_sibling: "Layout") -> None:
        self.node = node
        self.parent = parent
        self.previous_sibling = previous_sibling
        self.children: list[Layout] = []

        self.line: list[TextInLine] = []
        self.display_list: list[TextStyle] = []

        self.abs_x: float = 0
        self.abs_y: float = 0
        self.rel_x: float = 0  # offset from abs_x within the block
        self.rel_y: float = 0  # offset from abs_y within the block
        self.block_width: float = 0
        self.block_height: float = 0

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

    def compute_block_height(self, mode: Literal["block", "inline"]):
        #  A block that contains other blocks should be tall enough to contain all of its children, so its height should be the sum of its children’s heights
        if mode == "block":
            self.block_height = sum([child.block_height for child in self.children])
        # A block that contains text doesn’t have children; instead, it needs to be tall enough to contain all its text
        else:
            self.block_height = self.rel_y

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
            self.layout_leaf_block(self.node)
            # As usual with buffers, need to make sure the buffer is flushed once all tokens are processed
            self.flush()

        for child in self.children:
            child.layout()

        self.compute_block_height(mode)

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
                self.flush()

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
        color = node.style["color"]
        for word in node.text.split():
            # font = tkinter.font.Font(size=self.size, weight=self.weight, slant=self.style)
            font = self.get_font(node)
            word_width = font.measure(word)

            # Move to new line
            if self.rel_x + word_width > self.block_width:
                self.flush()

            self.line.append((self.rel_x, word, font, color))
            self.rel_x += word_width + font.measure(" ")

    def flush(self):
        """
        This method has three responsibilities:
        1. Align words along the line.
        2. Add all the words in the line to the display_list.
        3. Update the rel_x and rel_y positions.
        """
        # ? checks if 'self.line' is empty?
        if not self.line:
            return

        # Get the metrics for all the fonts on the line
        metrics = [font.metrics() for rel_x, word, font, color in self.line]

        # Find the tallest word
        max_ascent = max([metric["ascent"] for metric in metrics])

        # The line is then max_ascent below self.rel_y - or actually a little more to account for the leading
        baseline = self.rel_y + 1.25 * max_ascent

        # Place each word relative to that line
        for relative_x, word, font, color in self.line:
            x = self.abs_x + relative_x
            y = self.abs_y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font, color))

        self.line = []

        # Once line position is computed, reset the x, y coordinates
        self.rel_x = 0
        # 'rel_y' must be far enough below baseline to account for the deepest descender
        max_descent = max([metric["descent"] for metric in metrics])
        self.rel_y = baseline + 1.25 * max_descent

    def paint(self, display_list: list[DrawCommand]):
        """
        This method collect all the draw commands into the 'display_list'.

        Then 'Browser.draw()' can sequentially iterate over the commands and draw each command
        to the screen.
        """
        # display_list.extend(self.display_list)
        # * Can also change the 'display_field' to contain 'DrawText' commands directly
        for x, y, word, font, color in self.display_list:
            display_list.append(DrawText(x, y, word, font, color))

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
