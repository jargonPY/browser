import tkinter.font
from browser_html.html_nodes import Node

FONTS = {}


def get_tk_font_from_css_font(node: Node) -> tkinter.font.Font:
    weight = node.style["font-weight"]
    style = node.style["font-style"]

    # Convert CSS "normal" to Tk "roman"
    if style == "normal":
        style = "roman"

    # Convert CSS pixels to Tk points
    size = int(float(node.style["font-size"][:-2]) * 0.75)
    return get_font(size, weight, style)


def get_font(size, weight, slant) -> tkinter.font.Font:
    key = (size, weight, slant)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=slant)
        FONTS[key] = font
    return FONTS[key]
