import pytest
from browser_html.html_nodes import Element
from browser_css.css_rules import add_css_to_html_node
from browser_css.css_selectors import *


def test_style_rule_is_applied_to_node():
    node = Element("p", {"style": "color: green;"}, None)
    selector_rules = []

    add_css_to_html_node(node, selector_rules)

    assert "color" in node.style
    assert node.style["color"] == "green"


def test_tag_selector_rule_is_applied_to_node():
    html_tag = "p"
    node = Element(html_tag, {}, None)
    selector_rules = [(TagSelector(html_tag), {"color": "green"})]

    add_css_to_html_node(node, selector_rules)

    assert "color" in node.style
    assert node.style["color"] == "green"


def test_class_selector_rule_is_applied_to_node():
    css_class_name = "container"
    node = Element("p", {"class": css_class_name}, None)
    selector_rules = [(ClassSelector(css_class_name), {"color": "green"})]

    add_css_to_html_node(node, selector_rules)

    assert "color" in node.style
    assert node.style["color"] == "green"


def test_id_selector_rule_is_applied_to_node():
    id_name = "unique-id"
    node = Element("p", {"id": id_name}, None)
    selector_rules = [(IdSelector(id_name), {"color": "green"})]

    add_css_to_html_node(node, selector_rules)

    assert "color" in node.style
    assert node.style["color"] == "green"


def test_list_selector_rule_is_applied_to_node():
    html_tag = "p"
    node = Element(html_tag, {"style": "color: red;"}, None)
    selector_rules = [(ListSelector([html_tag, "div"]), {"color": "green"})]

    add_css_to_html_node(node, selector_rules)

    assert "color" in node.style
    assert node.style["color"] == "red"


def test_descendant_selector_rule_is_applied_to_node():
    ancestor_tag = "div"
    descendant_tag = "p"

    parent_node = Element(ancestor_tag, {}, None)
    node = Element(descendant_tag, {}, parent_node)

    ancestor = TagSelector(ancestor_tag)
    descendant = TagSelector(descendant_tag)
    selector_rules = [(DescendantSelector(ancestor, descendant), {"color": "green"})]

    add_css_to_html_node(node, selector_rules, inherited_rules={})

    assert "color" in node.style
    assert node.style["color"] == "green"


def test_descendant_selector_rule_is_applied_to_a_nested_node():
    ancestor_tag = "div"
    descendant_tag = "p"

    grandparent_node = Element(ancestor_tag, {}, None)
    parent_node = Element("p", {}, grandparent_node)
    node = Element(descendant_tag, {}, parent_node)

    ancestor = TagSelector(ancestor_tag)
    descendant = TagSelector(descendant_tag)
    selector_rules = [(DescendantSelector(ancestor, descendant), {"color": "green"})]

    add_css_to_html_node(node, selector_rules, inherited_rules={})

    assert "color" in node.style
    assert node.style["color"] == "green"


def test_style_rule_overrides_selector_rule():
    html_tag = "p"
    node = Element(html_tag, {"style": "color: red;"}, None)
    selector_rules = [(TagSelector(html_tag), {"color": "green"})]

    add_css_to_html_node(node, selector_rules)

    assert "color" in node.style
    assert node.style["color"] == "red"


def test_multiple_selector_rules_are_applied_to_node():
    html_tag = "div"
    css_class_name = "container"
    node = Element(html_tag, {"style": "font-color: orange;", "class": css_class_name}, None)
    selector_rules = [
        (TagSelector(html_tag), {"background-color": "yellow"}),
        (ClassSelector(css_class_name), {"color": "red"}),
    ]

    add_css_to_html_node(node, selector_rules)

    # Test for tag selector rules
    assert "background-color" in node.style
    assert node.style["background-color"] == "yellow"

    # Test for class selector rules
    assert "color" in node.style
    assert node.style["color"] == "red"

    # Test for style attribute rules
    assert "font-color" in node.style
    assert node.style["font-color"] == "orange"
