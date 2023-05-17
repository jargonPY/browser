from typing import Union, TYPE_CHECKING
from browser_html.html_parser import Node
from browser_layout.layout import Layout
from draw_commands import DrawCommand

if TYPE_CHECKING:
    from browser_layout.block_layout import BlockLayout


class LineLayout(Layout):
    def __init__(self, node: Node, parent: "BlockLayout", previous_sibling: Union["LineLayout", None]) -> None:
        super().__init__(node, parent, previous_sibling)

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
