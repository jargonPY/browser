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

    def __init__(self, node: Node, parent: Node, previous_sibling: Node) -> None:
        self.node = node
        self.parent = parent
        self.previous_sibling = previous_sibling
        self.children: list[Layout] = []

        self.line: list[TextInLine] = []
        self.display_list: list[TextStyle] = []
        self.cursor_x: float = Layout.H_STEP
        self.cursor_y: float = Layout.V_STEP
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

    def layout(self):
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
            if self.cursor_x + word_width > self.WIDTH - self.H_STEP:
                self.flush()
                # self.cursor_x = self.H_STEP
                # self.cursor_y += font.metrics("linespace") * 1.25

            self.line.append((self.cursor_x, word, font))
            # self.display_list.append((self.cursor_x, self.cursor_y, word, font))
            self.cursor_x += word_width + font.measure(" ")

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
        metrics = [font.metrics() for cursor_x, word, font in self.line]

        # Find the tallest word
        max_ascent = max([metric["ascent"] for metric in metrics])

        # The line is then max_ascent below self.y—or actually a little more to account for the leading
        baseline = self.cursor_y + 1.25 * max_ascent

        # Place each word relative to that line
        for cursor_x, word, font in self.line:
            cursor_y = baseline - font.metrics("ascent")
            self.display_list.append((cursor_x, cursor_y, word, font))

        self.line = []
        self.cursor_x = Layout.H_STEP
        # 'cursor_y' must be far enough below baseline to account for the deepest descender
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent


class DocumentLayout:
    def __init__(self, node: Node) -> None:
        self.node = node
        self.parent = None
        self.children: list[Layout] = []

    def layout(self):
        child = Layout(self.node, self, None)
        self.children.append(child)
        child.layout()
        self.display_list = child.display_list
