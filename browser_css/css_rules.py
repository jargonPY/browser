from typing import TYPE_CHECKING
from browser_css.css_parser import CSSParser
from browser_css.css_selectors import *
from utils.constants import INHERITED_PROPERTIES

if TYPE_CHECKING:
    from utils.type_hints import CSSRule


def cascade_priority(rule: "CSSRule") -> int:
    selector, body = rule
    return selector.prioroty


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
    if property == "font_size":
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
        # * Returns 'None' for 'font_size' that is not handled (ex. 'rem')
        else:
            return None
    return value


def add_css_to_html_node(node: Node, rules: list["CSSRule"]) -> None:
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
    for property, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value

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

    # Add class attribute rules
    if isinstance(node, Element) and "class" in node.attributes:
        # todo need to iterate over every rule and add the ones that match the class_name
        node.css_class_name = node.attributes["class"]

    # Add style attribute rules
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            computed_value = compute_style(node, property, value)
            if not computed_value:
                continue
            node.style[property] = computed_value

    for child in node.children:
        add_css_to_html_node(child, rules)
