import pytest
from browser_css.css_parser import CSSParser
from browser_css.css_selectors import *


@pytest.fixture
def css_parser():
    # Create an instance of CSSParser for testing
    text = """
    body {
        color: red;
        background-color: white;
    }
    """
    return CSSParser(text)


def test_is_end(css_parser):
    assert css_parser.is_end() == False
    css_parser.index = len(css_parser.text)
    assert css_parser.is_end() == True


def test_ignore_until(css_parser):
    assert css_parser.ignore_until(["{"]) == "{"


def test_ignore_until_end_of_file(css_parser):
    assert css_parser.ignore_until(["random"]) == None


def test_white_space():
    text = "First" + " " * 10 + "Second"
    css_parser = CSSParser(text)
    css_parser.index = 6
    css_parser.white_space()
    assert css_parser.index == 15


def test_word(css_parser):
    assert css_parser.word() == "body"


def test_literal(css_parser):
    css_parser.literal("b")
    assert css_parser.index == 1
    with pytest.raises(AssertionError):
        css_parser.literal("z")


def test_property_value_pair(css_parser):
    text = "color: red;"
    css_parser = CSSParser(text)
    assert css_parser.property_value_pair() == ("color", "red")

    text = "background-color:white;"
    css_parser = CSSParser(text)
    assert css_parser.property_value_pair() == ("background-color", "white")

    text = "background-color: white;"
    css_parser = CSSParser(text)
    assert css_parser.property_value_pair() == ("background-color", "white")


def test_body(css_parser):
    text = """
            color: red;
            background-color: white;
            """
    css_parser = CSSParser(text)
    assert css_parser.body() == {"color": "red", "background-color": "white"}


def test_selector(css_parser):
    assert css_parser.selector() == TagSelector("body")


def test_parse_css_file(css_parser):
    assert css_parser.parse_css_file() == [(TagSelector("body"), {"color": "red", "background-color": "white"})]
