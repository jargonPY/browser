from typing import Tuple, List, Literal
import tkinter.font
from html_parser import Node, Element, Text


class Layout:
    WIDTH, HEIGHT = 800, 600
    H_STEP, V_STEP = 13, 18

    def __init__(self) -> None:
        self.display_list: List[Tuple[float, float, str, tkinter.font.Font]] = []
        self.cursor_x: float = Layout.H_STEP
        self.cursor_y: float = Layout.V_STEP
        self.weight: Literal["normal", "bold"] = "normal"
        self.style: Literal["roman", "italic"] = "roman"
        self.size = 16

    def layout(self, tree_node: Node):
        self.layout_html_tree(tree_node)
        return self.display_list

    def layout_html_tree(self, tree_node: Node) -> None:
        if isinstance(tree_node, Text):
            self.text(tree_node)
        elif isinstance(tree_node, Element):
            self.open_tag(tree_node.tag)
            for child in tree_node.children:
                self.layout(child)
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
                self.cursor_x = self.H_STEP
                self.cursor_y += font.metrics("linespace") * 1.25

            self.display_list.append((self.cursor_x, self.cursor_y, word, font))
            self.cursor_x += word_width + font.measure(" ")
