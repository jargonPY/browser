from typing import TYPE_CHECKING
from browser_css.css_parser import CSSParser
from browser_css.css_selectors import *
from utils.constants import INHERITED_PROPERTIES

if TYPE_CHECKING:
    from utils.type_hints import CSSRule


def cascade_priority(rule: "CSSRule") -> int:
    selector, body = rule
    return selector.priority


def sort_rules_by_priority(rules: list["CSSRule"]) -> list["CSSRule"]:
    return sorted(rules, key=cascade_priority)


def compute_style(node: Node, property: str, value: str) -> str | None:
    """
    This method is used to resolve percentages to absolute pixel units.

    The issue:
    Inheriting font size comes with a twist. Web pages can use percentages as font sizes: h1 { font-size: 150% }
    makes headings 50% bigger than surrounding text. But what if you had, say, a code element inside an h1
    tag — would that inherit the 150% value for font-size? Surely it shouldn’t be another 50% bigger than the
    rest of the heading text.

    So, in fact, browsers resolve percentages to absolute pixel units before storing them in the style and before
    those values are inherited; it’s called a “computed style”.
    """
    if property == "font-size":
        if value.endswith("px"):
            return value
        elif value.endswith("%"):
            """
            Percentage sizes also have to handle a tricky edge case: percentage sizes for the root html element.
            In that case the percentage is relative to the default font size.
            """
            if node.parent:
                parent_font_size = node.parent.style["font-size"]
            else:
                parent_font_size = INHERITED_PROPERTIES["font-size"]
            node_pct = float(value[:-1]) / 100
            parent_px = float(parent_font_size[:-2])
            return str(node_pct * parent_px) + "px"
        elif value.endswith("rem"):
            """
            Root em is a relative unit, which means it is calculated based on the root font size. The root font size is
            typically set on the <html> element of the document. By default, the root font size is usually 16 pixels,
            so if you set a font size to 1rem, it will be equal to 16 pixels. However, the key difference is that if
            you change the root font size, all rem values in the document will be adjusted accordingly.
            """
            # todo handle the case where root font size is changed by the user rather than hardcoded by 'INHERITED_PROPERTIES'
            root_font_size = INHERITED_PROPERTIES["font-size"]
            node_font_size = float(value[:-3]) * float(root_font_size[:-2])
            return str(node_font_size) + "px"
        elif value.endswith("em"):
            """
            Similar to rem but it calculates sizes based on the parent element's font size rather than the root font size.
            """
            # todo this calculation for 'em' is incorrect, find the exact rules of how 'em' is calculated
            if node.parent:
                parent_font_size = node.parent.style["font-size"]
            else:
                parent_font_size = INHERITED_PROPERTIES["font-size"]
            node_font_size = float(value[:-3]) * float(parent_font_size[:-2])
            return str(node_font_size) + "px"
        # * Returns 'None' for 'font_size' that is not handled (ex. 'rem')
        else:
            return None
    return value


def add_css_to_html_node(node: Node, rules: list["CSSRule"], inherited_rules=INHERITED_PROPERTIES) -> None:
    """
    Recursively adds css styles based on the rules provided to a node and its children.

    Since several rules can apply to the same element, there is a rule order (i.e. cascade order)
    that determines which rules take priority, thus overriding the other rules when they clash.

    From lowest to highest priority:
    1. Inherited rules - These are the rules that get inherited from the parent if the node doesn't have
                         a value for a certain property.
                         For example 'Text' nodes don't have any styling properties set on them so they inherit
                         all their properties.
                         Note not all properties are inherited, the properties that should be inherited are
                         defined in 'INHERITED_PROPERTIES'.

    2. Selector rules - These rules are defined in a css file. These come before the rules defined in the
                        'style' attribute, since the 'style' attribute has the highest precedence.
                        If two files both defined rules for the same selector, the file order - that is
                        which file was imported/parsed first - acts as the tie braker.
                        This system allows more specific rules to override more general ones, so that you
                        can have a browser style sheet, a site-wide style sheet, and maybe a special style
                        sheet for a specific web page, all co-existing.

    3. Style attribute rules.
    """

    # Add inherited rules
    for property, default_value in inherited_rules.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value

    # todo update so that even the low priority selectors override the browser default rules
    # Add selector rules
    for selector, body in rules:
        if not selector.matches(node):
            continue

        for property, value in body.items():
            computed_value = compute_style(node, property, value)
            # * Subtle choice here, this skips any properties that 'compute_style' doesn't know how to handle.
            if not computed_value:
                continue
            node.style[property] = computed_value

    # # Add style attribute rules
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).parse_body()
        for property, value in pairs.items():
            computed_value = compute_style(node, property, value)
            if not computed_value:
                continue
            node.style[property] = computed_value

    for child in node.children:
        add_css_to_html_node(child, rules)
