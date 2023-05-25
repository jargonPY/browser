from browser_layout.block_layout import BlockLayout
from browser_html.html_parser import Node
from draw_commands import DrawCommand
from browser_config import WINDOW_WIDTH, H_STEP, V_STEP


class DocumentLayout:
    def __init__(self, html_tree: Node) -> None:
        self.node = html_tree
        self.parent = None
        self.children: list[BlockLayout] = []

        # Layout of the main page
        self.abs_x = H_STEP
        self.abs_y = V_STEP
        self.block_width = WINDOW_WIDTH - 2 * H_STEP

    def layout(self):
        child = BlockLayout(self.node, self, None)
        child.layout()

        self.block_height = child.block_height + 2 * V_STEP
        self.children.append(child)

    def paint(self, display_list: list[DrawCommand]):
        self.children[0].paint(display_list)
