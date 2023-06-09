from typing import Literal, TYPE_CHECKING
from browser_layout.layout import Layout
from loguru import logger

if TYPE_CHECKING:
    from browser_layout.text_layout import TextLayout

"""
When you set the width and height properties of an element with CSS, you just set the width and height of the content area.
To calculate the full size of an element, you must also add padding, borders and margins.

Total element width = width + left padding + right padding + left border + right border + left margin + right margin

Total element height = height + top padding + bottom padding + top border + bottom border + top margin + bottom margin

The order the values are written will determine which sides each applies to:
- Two values apply to the top and bottom, then right and left.
- Three values apply to the top, then right and left, then bottom.
- Four values apply to the top, then right, then bottom, then left.
"""

BoxType = Literal["block", "inline", "line", "text"]


def compute_box_width(box: Layout, box_type: BoxType):
    if box_type == "block":
        # Blocks are as wide as their parents
        box.block_width = box.parent.block_width

    elif box_type == "line":
        # Lines are as wide as their parents
        box.block_width = box.parent.block_width

    elif box_type == "inline":
        # todo need to use the font of the child 'TextLayout'
        space = box.font.measure(" ")
        box.block_width = sum([child.block_width for child in box.children]) + space * (len(box.children))

    elif box_type == "text":
        box.block_width = box.font.measure(box.word)


def compute_box_height(box: Layout, box_type: BoxType):
    if box_type == "block":
        # todo this method has certain preconditions that must be true, either include them as a doc string document or explicitly check/validate them
        # todo for example to compute the 'block_height' all of its children heights must be computed first
        # Compute the height of a paragraph of text by summing the height of its lines
        box.block_height = sum([child.block_height for child in box.children]) + box.margin.top + box.margin.bottom

    elif box_type == "line":
        words: list["TextLayout"] = []
        for inline_box in box.children:
            for word in inline_box.children:
                words.append(word)
        max_ascent = max([word.font.metrics("ascent") for word in words]) if len(words) > 0 else 0
        baseline = box.abs_y + 1.25 * max_ascent
        for word in words:
            word.abs_y = baseline - word.font.metrics("ascent")
        # ? Should a line be created if it doesn't have any children?
        max_descent = max([word.font.metrics("descent") for word in words]) if len(words) > 0 else 0

        box.block_height = 1.25 * (max_ascent + max_descent)
        for inline_box in box.children:
            inline_box.block_height = box.block_height

    elif box_type == "inline":
        # Inline box height is set by the Line box (see above)
        pass

    elif box_type == "text":
        box.block_height = box.font.metrics("linespace")


def compute_box_x_position(box: Layout, box_type: BoxType):
    if box_type == "block":
        # The block starts at its parent's left edge
        box.abs_x = box.parent.abs_x

    elif box_type == "line":
        box.abs_x = box.parent.abs_x

    elif box_type == "inline":
        if box.previous_sibling is not None:
            # space = box.previous_sibling.font.measure(" ")
            box.abs_x = box.previous_sibling.abs_x + box.previous_sibling.block_width
        else:
            box.abs_x = box.parent.abs_x

    elif box_type == "text":
        if box.previous_sibling is not None:
            space = box.previous_sibling.font.measure(" ")
            box.abs_x = box.previous_sibling.abs_x + space + box.previous_sibling.block_width
        else:
            box.abs_x = box.parent.abs_x


def compute_box_y_position(box: Layout, box_type: BoxType):
    if box_type == "block":
        # Vertical position depends on the position and height of their previous sibling
        if box.previous_sibling:
            box.abs_y = box.previous_sibling.y_bottom + box.margin.top
        # If there is no previous siblng, the block starts at the paren'ts top edge
        else:
            box.abs_y = box.parent.abs_y + box.margin.top

    elif box_type == "line":
        if box.previous_sibling is not None:
            box.abs_y = box.previous_sibling.abs_y + box.previous_sibling.block_height
        else:
            box.abs_y = box.parent.abs_y

    elif box_type == "inline":
        box.abs_y = box.parent.abs_y

    elif box_type == "text":
        # Text box 'abs_y' is set by the Line box when it computes height (see 'compute_box_height' above)
        pass
