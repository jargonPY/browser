from typing import Tuple, Literal
import tkinter.font
from html_parser import Node, Element, Text

# A list of all the tags that describe parts of a page instead of formatting
BLOCK_ELEMENTS = [
    "html",
    "body",
    "article",
    "section",
    "nav",
    "aside",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hgroup",
    "header",
    "footer",
    "address",
    "p",
    "hr",
    "pre",
    "blockquote",
    "ol",
    "ul",
    "menu",
    "li",
    "dl",
    "dt",
    "dd",
    "figure",
    "figcaption",
    "main",
    "div",
    "table",
    "form",
    "fieldset",
    "legend",
    "details",
    "summary",
]


TextInLine = Tuple[float, str, tkinter.font.Font]

TextStyle = Tuple[float, float, str, tkinter.font.Font]


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

        self.rel_x: float = 0  # offset from abs_x within the block
        self.rel_y: float = 0  # offset from abs_y within the block
        self.block_width: float = 0
        self.block_height: float = 0

        self.weight: Literal["normal", "bold"] = "normal"
        self.style: Literal["roman", "italic"] = "roman"
        self.size = 16

    def layout_mode(self, tree_node: Node):
        if isinstance(tree_node, Text):
            return "inline"
        elif tree_node.children:
            if any([isinstance(child, Element) and child.tag in BLOCK_ELEMENTS for child in tree_node.children]):
                return "block"
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

        for child in self.children:
            self.display_list.extend(child.display_list)

        self.compute_block_height(mode)

    def layout_intermediate_block(self):
        previous = None
        # ? Constructs a Layout for all children regardless if they are a "block" or "inline" element?
        """
        Our layout_mode function has to handle one tricky case, where a node contains both block children like
        a <p> element but also text children like a text node or a <b> element. I’ve chosen to use block mode
        in this case, but it’s probably best to think of this as a kind of error on the part of the web developer.
        And just like with implicit tags in Chapter 4, we use a repair mechanism to make sense of the situation.
        """
        for child in self.node.children:
            # Constructs a Layout from an Element node, using the previous child as the sibling argument
            next = Layout(child, self, previous)
            # Append the child Layout object to this (parent) array of children
            self.children.append(next)
            # Store the child ot be used as the previous sibling
            previous = next

    def layout_leaf_block(self, tree_node: Node):
        if isinstance(tree_node, Text):
            self.text(tree_node)
        elif isinstance(tree_node, Element):
            self.open_tag(tree_node.tag)
            for child in tree_node.children:
                # ? Assumes that all children of a non-block ("inline") element are also non-block elements?
                self.layout_leaf_block(child)
            self.close_tag(tree_node.tag)

    def open_tag(self, tag: str) -> None:
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4

    def close_tag(self, tag: str) -> None:
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.size += 2
        elif tag == "big":
            self.size -= 4

    def text(self, token: Text) -> None:
        for word in token.text.split():
            font = tkinter.font.Font(size=self.size, weight=self.weight, slant=self.style)
            word_width = font.measure(word)

            # Move to new line
            if self.rel_x + word_width > self.block_width:
                self.flush()

            self.line.append((self.rel_x, word, font))
            self.rel_x += word_width + font.measure(" ")

    def flush(self):
        """
        This method has three responsibilities:
        1. Align words along the line.
        2. Add all the words in the line to the display_list.
        3. Update the x and y positions.
        """
        # ? checks if 'self.line' is empty?
        if not self.line:
            return

        # Get the metrics for all the fonts on the line
        metrics = [font.metrics() for rel_x, word, font in self.line]

        # Find the tallest word
        max_ascent = max([metric["ascent"] for metric in metrics])

        # The line is then max_ascent below self.rel_y - or actually a little more to account for the leading
        baseline = self.rel_y + 1.25 * max_ascent

        # Place each word relative to that line
        for relative_x, word, font in self.line:
            x = self.abs_x + relative_x
            y = self.abs_y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        self.line = []

        # Once line position is computed, reset the x, y coordinates
        self.rel_x = 0
        # 'rel_y' must be far enough below baseline to account for the deepest descender
        max_descent = max([metric["descent"] for metric in metrics])
        self.rel_y = baseline + 1.25 * max_descent


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
        self.display_list = child.display_list
