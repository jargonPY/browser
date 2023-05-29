import copy
from typing import Union
from browser_layout.layout import Layout
from browser_html.html_parser import Node, Element, Text
from browser_layout.line_layout import LineLayout
from browser_layout.inline_layout import InlineLayout
from browser_layout.text_layout import TextLayout
from draw_commands import DrawCommand, DrawRect
from utils.fonts_cache import get_tk_font_from_css_font
from loguru import logger
from browser_layout.box_position import (
    compute_box_height,
    compute_box_width,
    compute_box_x_position,
    compute_box_y_position,
)


class BlockLayout(Layout):
    def __init__(self, node: Node, parent: "BlockLayout", previous_sibling: Union["BlockLayout", None]) -> None:
        super().__init__(node, parent, previous_sibling)
        self.previous_word: "TextLayout" | None = None

        self.rel_x: float = 0  # offset from abs_x within the block
        self.rel_y: float = 0  # offset from abs_y within the block

    def layout(self):
        """
        Layout steps:
        1. Compute the 'width', 'abs_x', and 'abs_y' fields from the 'parent' and 'previous_sibling' fields.
        2. Create layout object for each child element.
        3. Layout the children nodes by calling their layout method recursively.
        4. Compute the 'height' field based on the child node heights.
        """

        # todo move position computation into a seperate function and combine with other box types (this will centralize all position computations)
        compute_box_width(self, "block")
        compute_box_x_position(self, "block")
        compute_box_y_position(self, "block")

        """
        Block box - can have either all block-level elements as children or all inline-level elements, but not both.
        Inline box - can only have inline-level elements as children.

        This portion is responsible for wrapping the HTML nodes into "boxes", which define the layout rules
        that will be applied to an element (i.e. a block box will have different layout rules than an inline box).
        """

        # todo if a block-level element has both block and inline children, rather than treat each inline element
        # todo as block element, create a single block that wraps the inline elements

        """
        Ex.

        <p>
            Hello
            <span>span</span>
            <p>There</p>
        </p>

        Block(p)
            AnonBlock()
                Inline(Hello)
                Inline(span)
            Block(p)
        """

        block_child_nodes = [child for child in self.node.children if self.layout_mode(child) == "block"]

        if len(block_child_nodes) > 0:
            self.layout_block()
        else:
            self.new_line()
            self.layout_inline(self.node)

        for child in self.children:
            child.layout()

        compute_box_height(self, "block")

    def paint(self, display_list: list[DrawCommand]):
        if isinstance(self.node, Element):
            bg_color = self.node.style.get("background-color", "transparent")
            if bg_color != "transparent":
                x2, y2 = self.abs_x + self.block_width, self.abs_y + self.block_height
                rect = DrawRect(self.abs_x, self.abs_y, x2, y2, bg_color)
                display_list.append(rect)

        for child in self.children:
            child.paint(display_list)

    def layout_mode(self, html_node: Node):  # -> Literal["block", "inline"]:
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

    def compute_block_width(self):
        # Blocks are as wide as their parents
        self.block_width = self.parent.block_width

    def compute_block_height(self) -> None:
        """
        Compute the height of a paragraph of text by summing the height of its lines.
        """
        self.block_height = sum([child.block_height for child in self.children])

    def layout_block(self):
        previous = None
        anonymous_block_children = []
        for child in self.node.children:
            if self.layout_mode(child) == "inline":
                anonymous_block_children.append(child)
                continue

            if self.layout_mode(child) == "block" and len(anonymous_block_children) > 0:
                node = copy.deepcopy(self.node)
                node.children = anonymous_block_children
                next = BlockLayout(node, self, previous)
                self.children.append(next)
                previous = next
                anonymous_block_children = []
            # Constructs a Layout from an Element node, using the previous child as the sibling argument
            next = BlockLayout(child, self, previous)
            # Append the child Layout object to this (parent) array of children
            self.children.append(next)
            # Store the child ot be used as the previous sibling
            previous = next

        if len(anonymous_block_children) > 0:
            node = copy.deepcopy(self.node)
            node.children = anonymous_block_children
            next = BlockLayout(node, self, previous)
            self.children.append(next)

    def layout_inline(self, node: Node):
        if isinstance(node, Text):
            self.layout_text(node)

        elif isinstance(node, Element):
            if node.tag == "br":
                self.new_line()

            for child in node.children:
                self.layout_inline(child)

    def layout_text(self, node: Text) -> None:
        line = self.children[-1]
        if len(line.children) > 0:
            inline_layout = InlineLayout(node, line, line.children[-1])
        else:
            inline_layout = InlineLayout(node, line, None)
        line.children.append(inline_layout)
        for word in node.text.split():
            font = get_tk_font_from_css_font(node)
            word_width = font.measure(word)

            # Move to new line
            if self.rel_x + word_width > self.block_width:
                self.new_line()
                line = self.children[-1]
                inline_layout = InlineLayout(node, line, None)
                line.children.append(inline_layout)

            # The LineLayouts are children of the BlockLayout, so the current line can be found at the end of the children array
            # line = self.children[-1]
            text = TextLayout(node, inline_layout, self.previous_word, word)
            inline_layout.children.append(text)
            self.previous_word = text

            self.rel_x += word_width + font.measure(" ")

    def new_line(self) -> None:
        self.previous_word = None
        self.rel_x = 0
        last_line = self.children[-1] if self.children else None

        # todo replace assertion with a different type checking mechanism
        # assert (
        #     isinstance(last_line, LineLayout) or last_line is None
        # ), f"Expected 'last_line' to be of type 'LineLayout' or 'None', received {type(last_line)} instead"

        new_line = LineLayout(self.node, self, last_line)
        self.children.append(new_line)

    def __repr__(self) -> str:
        return f"< Block abs_x={self.abs_x} abs_y={self.abs_y} rel_x={self.rel_x} rel_y={self.rel_y} style={self.node.style} >"
