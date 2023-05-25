from browser_layout.document_layout import DocumentLayout
from browser_layout.block_layout import BlockLayout
from browser_html.html_parser import Node
from draw_commands import DrawCommand


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


def build_render_tree(node: Node, parent_block: BlockLayout | None, sibling_block: BlockLayout | None):
    """
    Block box - can have either all block-level elements as children or all inline-level elements, but not both.
    Inline box - can only have inline-level elements as children.

    This method is responsible for wrapping the HTML nodes into "boxes", which define the layout rules
    that will be applied to an element (i.e. a block box will have different layout rules than an inline box).
    """

    # Handle the case of the initial root node
    if parent_block is None:
        root = DocumentLayout(node)
    else:
        root = BlockLayout(node, parent_block, sibling_block)

    block_child_nodes = [child for child in node.children if layout_mode(child) == "block"]

    # If any of the children is a block-level element, than all children will be considered as block-level elements and wrapped in a block box
    if len(block_child_nodes) > 0:
        previous = None
        for child in node.children:
            # Constructs a Layout from an Element node, using the previous child as the sibling argument
            next = BlockLayout(child, root, previous)
            # Append the child Layout object to this (parent) array of children
            root.children.append(next)
            # Store the child ot be used as the previous sibling
            previous = next
    # Otherwise all children are assumed to be inline-level elements, and wrapped in a inline box
    else:
        previous = None
        for child in node.children:
            # Constructs a Layout from an Element node, using the previous child as the sibling argument
            next = InlineLayout(child, root, previous)
            # Append the child Layout object to this (parent) array of children
            root.children.append(next)
            # Store the child ot be used as the previous sibling
            previous = next

    # ? Should this only be done for nodes whose children are block-level elements?
    previous_child = None
    for child in node.children:
        build_render_tree(child, root, previous_child)
        previous_child = child


def build_line_blocks(block_box: BlockLayout):
    """
    Input - a block box whose children all inline boxes.

    Need to remove all inline box children for block_box and replace it with
    line box children, whose in turn store the inline box children.
    """

    line = LineLayout(block_box.node, block_box, None)
    for child in block_box.children:
        if isinstance(child.node, Text):
            layout_text(node)

        elif isinstance(child.node, Element):
            if child.node.tag == "br":
                new_line()

            # * Assumes that the children of an inline block are all inline blocks
            # for child in child.node.children:
            #     build_line_blocks(child)


# def build_render_tree(node: Node):
#     """
#     1. If an element is a block-level element, create a block box whose children must be either
#        all block-level boxes or all inline-level boxes but not both.
#     2. If an element is a inline-level element, all of its children must be inline-level
#        elements (i.e. don't allow block-level elements inside inline-level elements).
#     """

#     root = BlockLayout(node)

#     previous = None
#     for child in node.children:
#         display_mode = layout_mode(node)

#         if display_mode == "block":
#             # Constructs a Layout from an Element node, using the previous child as the sibling argument
#             next = BlockLayout(child, root, previous)
#             # Append the child Layout object to this (parent) array of children
#             root.children.append(next)
#             # Store the child ot be used as the previous sibling
#             previous = next

#         elif display_mode == "inline":
#             """
#             Inline boxes are generated during the box generation phase, while line boxes are created
#             during the inline formatting process.

#             The goal of an inline element is to wrap a piece of text in a tag which allows a user to define
#             styles for a portion of a text. 'Text' node inherits the properties of its parent element.
#             So to render we can extract the 'Text' nodes from every inline element and work with that.
#             """
#             if isinstance(child, Text):
#                 # * Wrap it in an anyonmous box (block or inline will depened on the other children)
#                 # ? Can 'TextLayout' be used? 'TextLayout' represents a single word rather than a run of text.
#                 pass
#             else:
#                 # * Drill into the element to extract its 'Text' nodes.
#                 pass
#             continue


# def build_layout_tree(node: Node):
#     # Create the root box
#     mode = layout_mode(node)
#     if mode == "block":
#         root = BlockLayout(node)
#     """
#     for child in &style_node.children {
#         match child.display() {
#             Block => root.children.push(build_layout_tree(child)),
#             Inline => root.get_inline_container().children.push(build_layout_tree(child)),
#             DisplayNone => {} // Skip nodes with `display: none;`
#         }
#     }
#     return root;
#     """
#     # Create the descendant boxes
#     pass


# def get_inline_container():
#     """
#     If a block node contains an inline child, create an anonymous block box to contain it.
#     If there are several inline children in a row, put them all in the same anonymous container.

#     # Where a new inline child should go.
#     match self.box_type {
#         InlineNode(_) | AnonymousBlock => self,
#         BlockNode(_) => {
#             # If we've just generated an anonymous block box, keep using it.
#             # Otherwise, create a new one.
#             match self.children.last() {
#                 Some(&LayoutBox { box_type: AnonymousBlock,..}) => {}
#                 _ => self.children.push(LayoutBox::new(AnonymousBlock))
#             }
#             self.children.last_mut().unwrap()
#         }
#     }
#     """
#     pass


from typing import Union, TYPE_CHECKING

# from typing import Union
# from browser_layout.layout import Layout
# from browser_html.html_parser import Node, Element, Text
# from browser_layout.line_layout import LineLayout
# from browser_layout.text_layout import TextLayout
# from draw_commands import DrawCommand
# from utils.fonts_cache import get_tk_font_from_css_font

# if TYPE_CHECKING:
#     from browser_layout.block_layout import BlockLayout


# def get_current_line(current_node: Node, parent_block: "BlockLayout") -> LineLayout:
#     if len(parent_block.children) > 0 and isinstance(parent_block.children[-1], LineLayout):
#         return parent_block.children[-1]
#     else:
#         return LineLayout(current_node, parent_block, None)


# class InlineLayout(Layout):
#     def __init__(self, node: Node, parent: "BlockLayout", previous_sibling: Union["Layout", None]) -> None:
#         super().__init__(node, parent, previous_sibling)
#         self.current_line: "LineLayout" | None = get_current_line(node, parent)
#         self.previous_word: "TextLayout" | None = parent.previous_word

#     def layout(self) -> None:
#         if isinstance(self.node, Text):
#             self.layout_text(self.node)

#         elif isinstance(self.node, Element):
#             if self.node.tag == "br":
#                 self.new_line()

#             for child in self.node.children:
#                 child.layout()

#     def paint(self, display_list: list[DrawCommand]) -> None:
#         for child in self.children:
#             child.paint(display_list)

#     def layout_text(self, node: Text) -> None:
#         for word in node.text.split():
#             font = get_tk_font_from_css_font(node)
#             word_width = font.measure(word)

#             # Move to new line
#             if self.rel_x + word_width > self.block_width:
#                 self.new_line()

#             # The LineLayouts are children of the BlockLayout, so the current line can be found at the end of the children array
#             line = self.children[-1]
#             text = TextLayout(node, line, self.previous_word, word)
#             line.children.append(text)
#             self.previous_word = text

#             self.rel_x += word_width + font.measure(" ")

#     def new_line(self) -> None:
#         self.previous_word = None
#         self.rel_x = 0
#         last_line = self.children[-1] if self.children else None

#         # todo replace assertion with a different type checking mechanism
#         # assert (
#         #     isinstance(last_line, LineLayout) or last_line is None
#         # ), f"Expected 'last_line' to be of type 'LineLayout' or 'None', received {type(last_line)} instead"

#         new_line = LineLayout(self.node, self, last_line)
#         self.children.append(new_line)
