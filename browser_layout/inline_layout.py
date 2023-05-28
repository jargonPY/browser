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


class InlineLayout(Layout):
    def __init__(self, node: Node, parent: "LineLayout", previous_sibling: Union["InlineLayout", None]) -> None:
        super().__init__(node, parent, previous_sibling)

    def layout(self) -> None:
        # * do not set 'self.block_height', it is set by 'LineLayout' after aligning the font for the entire line
        self.font = get_tk_font_from_css_font(self.node)
        self.abs_y = self.parent.abs_y

        if self.previous_sibling is not None:
            space = self.previous_sibling.font.measure(" ")
            self.abs_x = self.previous_sibling.abs_x + self.previous_sibling.block_width
        else:
            self.abs_x = self.parent.abs_x

        for word in self.children:
            word.layout()

        # todo need to use the font of the child 'TextLayout'
        space = self.font.measure(" ")
        self.block_width = sum([child.block_width for child in self.children]) + space * (len(self.children))

    def paint(self, display_list: list[DrawCommand]) -> None:
        # * Apply styles from the parent inline element
        # todo this works backwards up the node tree, this is not a proper solution
        parent_node = self.node.parent
        while layout_mode(parent_node) == "inline":
            bg_color = parent_node.style.get("background-color", "transparent")
            if bg_color != "transparent":
                x2, y2 = self.abs_x + self.block_width, self.abs_y + self.block_height
                rect = DrawRect(self.abs_x, self.abs_y, x2, y2, bg_color)
                display_list.append(rect)
                # * Applies the style of the closest inline ancestor
                break
            parent_node = parent_node.parent

        for child in self.children:
            child.paint(display_list)

    def __repr__(self) -> str:
        return (
            f"< Inline abs_x={self.abs_x} abs_y={self.abs_y} style={self.node.style} p={layout_mode(self.node.parent)}>"
        )
