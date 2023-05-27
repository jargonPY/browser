from browser_layout.block_layout import BlockLayout
from browser_html.html_parser import Node
from draw_commands import DrawCommand
from browser_config import WINDOW_WIDTH, H_STEP, V_STEP
from utils.utils import print_tree, stringify_tree
from loguru import logger


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
        # * Don't include any of the tags outside the 'body' in the render tree as those are usually used for metadata
        for child in self.node.children:
            if child.tag != "body":
                continue

            child = BlockLayout(child, self, None)
            child.layout()

        self.block_height = child.block_height + 2 * V_STEP
        self.children.append(child)

        logger.debug(stringify_tree(self))

    def paint(self, display_list: list[DrawCommand]):
        self.children[0].paint(display_list)

    def __repr__(self) -> str:
        return f"< Document abs_x={self.abs_x} abs_y={self.abs_y} style={self.node.style} >"
