import json
from typing import Tuple
from utils.type_hints import CSSPropertyName, CSSPropertyValue, CSSProperties, CSSRule
from browser_css.css_selectors import *
from loguru import logger


class CSSParser:
    def __init__(self, text: str) -> None:
        self.text = text.strip()  # Remove all trailing white space from the CSS file
        self.index = 0

    def is_end(self) -> bool:
        return self.index >= len(self.text)

    def ignore_until(self, chars: list[str]) -> str | None:
        """
        Parses a string until it reaches one of the characters passed in.

        This is used to discard substrings that are invalid:
        """
        while not self.is_end():
            char = self.text[self.index]
            if char in chars:
                return char
            else:
                self.index += 1
        return None

    def white_space(self):
        while not self.is_end() and self.text[self.index].isspace():
            self.index += 1

    def word(self) -> str:
        """
        Increments through word characters and returns the substring it parsed.
        """
        start = self.index
        while not self.is_end():
            char = self.text[self.index]
            if char.isalnum() or char in "#-.%":
                self.index += 1
            else:
                break
        """
        Parsing functions can fail. The word function we just wrote has an assertion to
        check that i advanced though at least one character—otherwise it didn’t point
        at a word to begin with.
        """
        assert self.index > start, f"Failed is 'word()', expected index: {self.index} needs to be greater than {start}."
        return self.text[start : self.index]

    def literal(self, literal: str):
        assert not self.is_end() and self.text[self.index] == literal, f"Expected {literal}"
        self.index += 1

    # def property_value_pair(self) -> Tuple[CSSPropertyName, CSSPropertyValue]:
    #     prop = self.word()
    #     self.white_space()
    #     self.literal(":")
    #     self.white_space()
    #     value = self.word()
    #     return prop.lower(), value

    def property_value_pair(self) -> Tuple[CSSPropertyName, CSSPropertyValue]:
        prop = self.word()
        value = ""
        self.white_space()
        self.literal(":")

        while not self.is_end() and self.text[self.index] != ";":
            self.white_space()
            # Add a space between values
            if len(value) > 0:
                value += " "
            value += self.word()

        return prop.lower(), value

    def parse_body(self) -> CSSProperties:
        """
        Parse CSS attributes into key, value pairs.

        Handles invalid css (whether it is bug by the author or not supported by our browwser)
        by skipping over the invalid substring to the next key, value pair.
        """
        pairs = {}
        while not self.is_end() and self.text[self.index] != "}":
            try:
                prop, value = self.property_value_pair()
                pairs[prop] = value
                self.white_space()
                self.literal(";")
                self.white_space()
            except AssertionError as e:
                # print("CSSParser AssertionError in body: ", e)
                current_char = self.ignore_until([";", "}"])
                # Skip to the next semicolon
                if current_char == ";":
                    self.literal(";")
                    self.white_space()
                # Or to the end of the string
                else:
                    break
        return pairs

    def parse_selector(self) -> Selector:
        selector_name = self.word().lower()
        tags = [selector_name]

        if selector_name.startswith("."):
            out: Selector = ClassSelector(selector_name.removeprefix("."))
        elif selector_name.startswith("#"):
            out = IdSelector(selector_name.removeprefix("#"))
        else:
            out = TagSelector(selector_name)

        self.white_space()
        while not self.is_end() and self.text[self.index] != "{":
            # Parse as list selector
            if self.text[self.index] == ",":
                self.literal(",")
                self.white_space()
                selector_name = self.word().lower()
                tags.append(selector_name)
                out = ListSelector(tags)
            # Parse as descendant selector
            else:
                selector_name = self.word().lower()
                if selector_name.startswith("."):
                    descendant: Selector = ClassSelector(selector_name.removeprefix("."))
                elif selector_name.startswith("#"):
                    out = IdSelector(selector_name.removeprefix("#"))
                else:
                    descendant = TagSelector(selector_name)

                out = DescendantSelector(out, descendant)
            self.white_space()
        return out

    def parse_css_file(self) -> list[CSSRule]:
        """
        A CSS file is a sequence of selectors and blocks (the rules to apply to a given selector).

        If there is an error parsing a selector, this method skips the entire rule.
        """
        rules: list[CSSRule] = []
        while not self.is_end():
            try:
                self.white_space()
                selector = self.parse_selector()
                self.literal("{")
                self.white_space()
                body = self.parse_body()
                self.literal("}")
                rules.append((selector, body))
            except AssertionError as e:
                # print("CSSParser AssertionError in parse_css_file: ", e)
                current_char = self.ignore_until(["}"])
                # Skip to the next semicolon
                if current_char == "}":
                    self.literal("}")
                    self.white_space()
                # Or to the end of the string
                else:
                    break
        # todo the logger below throws 'TypeError: Object of type TagSelector is not JSON serializable'
        # logger.debug(f"\nRules: {json.dumps(rules, indent=4)}\n")
        logger.debug(f"\nRules: {rules}\n")
        return rules
