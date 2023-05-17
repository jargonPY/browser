import tkinter.font
from typing import Union, TYPE_CHECKING
from browser_layout.layout import Layout
from browser_html.html_parser import Node
from draw_commands import DrawCommand, DrawText
from utils.fonts_cache import get_tk_font_from_css_font

if TYPE_CHECKING:
    from browser_layout.line_layout import LineLayout


class TextLayout(Layout):
    def __init__(
        self, node: Node, parent: "LineLayout", previous_sibling: Union["TextLayout", None], word: str
    ) -> None:
        super().__init__(node, parent, previous_sibling)
        self.word = word

    def layout(self) -> None:
        self.font = get_tk_font_from_css_font(self.node)

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
