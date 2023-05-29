from typing import TYPE_CHECKING
from dataclasses import dataclass
from loguru import logger

if TYPE_CHECKING:
    from browser_html.html_nodes import Node


@dataclass
class Margin:
    top: float = 0
    bottom: float = 0
    right: float = 0
    left: float = 0


def convert_to_px(value: str) -> float:
    if value.endswith("px"):
        return float(value.replace("px", ""))
    elif value.endswith("%"):
        pass
    # todo implement "rem" margin correctly
    elif value.endswith("rem"):
        return float(value.replace("rem", ""))
    # todo implement "em" margin correctly
    elif value.endswith("em"):
        return float(value.replace("em", ""))
    elif value == "auto":
        return 0
    return float(value)


def compute_margin_top(node: "Node") -> float:
    # todo 'px' should be resolved in 'css_rules' (similar to 'compute_style')
    if "margin-top" in node.style:
        margin_top = convert_to_px(node.style["margin-top"])
        return margin_top
    # 'margin': '40px 40px'
    elif "margin" in node.style:
        margin_top = convert_to_px(node.style["margin"].split()[0])
        return margin_top
    return 0


def compute_margin_bottom(node: "Node") -> float:
    if "margin-bottom" in node.style:
        margin_bottom = convert_to_px(node.style["margin-bottom"])
        return margin_bottom
    elif "margin" in node.style:
        margins = node.style["margin"].split()
        if len(margins) == 2:
            return convert_to_px(margins[0])
        if len(margins) == 3:
            return convert_to_px(margins[2])
        if len(margins) == 4:
            return convert_to_px(margins[2])
    return 0


def compute_margin_right(node: "Node") -> float:
    if "margin-right" in node.style:
        margin_right = float(node.style["margin-right"].replace("px", ""))
        return margin_right
    elif "margin" in node.style:
        margins = node.style["margin"].split()
        if len(margins) == 2:
            return convert_to_px(margins[1])
        if len(margins) == 3:
            return convert_to_px(margins[1])
        if len(margins) == 4:
            return convert_to_px(margins[1])
    return 0


def compute_margin_left(node: "Node") -> float:
    if "margin-left" in node.style:
        margin_left = float(node.style["margin-left"].replace("px", ""))
        return margin_left
    elif "margin" in node.style:
        margins = node.style["margin"].split()
        if len(margins) == 2:
            return convert_to_px(margins[1])
        if len(margins) == 3:
            return convert_to_px(margins[1])
        if len(margins) == 4:
            return convert_to_px(margins[3])
    return 0


def resolve_margin(node: "Node") -> Margin:
    top = compute_margin_top(node)
    bottom = compute_margin_bottom(node)
    right = compute_margin_right(node)
    left = compute_margin_left(node)
    return Margin(top, bottom, right, left)
