import tkinter.font
from typing import Union, TYPE_CHECKING
from browser_layout.layout import Layout
from browser_html.html_parser import Node
from draw_commands import DrawCommand, DrawText, DrawRect
from utils.fonts_cache import get_tk_font_from_css_font
from browser_html.html_parser import Node, Element, Text

if TYPE_CHECKING:
    from browser_layout.line_layout import LineLayout


def layout_mode(html_node: Node):  # -> Literal["block", "inline"]:
    if isinstance(html_node, Text):
        return "inline"

    if isinstance(html_node, Element):
        if "display" in html_node.style:
            return html_node.style["display"]
        else:
            # todo need to skip tags that are not rendered (ex. iframe, script)
            if len(html_node.children) == 0:
                print("Found Inline Node with No Children Nodes: ", html_node.tag)
            return "inline"

    # return "block"


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
        # * Apply styles from the parent inline element
        # todo this works backwards up the node tree, this is not a proper solution
        # todo this doesn't work for nested inline elements (although can be fixed with a loop walking up the tree)
        # todo this doesn't properly render runs of text (ex. background-color will be cut for every text box rather than smooth across several words)
        if layout_mode(self.node.parent) == "inline":
            bg_color = self.node.parent.style.get("background-color", "transparent")
            if bg_color != "transparent":
                x2, y2 = self.abs_x + self.block_width, self.abs_y + self.block_height
                rect = DrawRect(self.abs_x, self.abs_y, x2, y2, bg_color)
                display_list.append(rect)

        color = self.node.style["color"]
        display_list.append(DrawText(self.abs_x, self.abs_y, self.word, self.font, color))

    def __repr__(self) -> str:
        return (
            f"< Text abs_x={self.abs_x} abs_y={self.abs_y} style={self.node.style} p={layout_mode(self.node.parent)}>"
        )
