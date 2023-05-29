import html
import re
from utils.utils import print_tree, stringify_tree
from utils.constants import SELF_CLOSING_TAGS
from browser_html.html_nodes import *
from loguru import logger


class HTMLParser:
    def __init__(self, body: str) -> None:
        self.body = body
        self.unfinished: list[Node] = []

    def parse(self):
        """
        Return the text-not-tags content of the HTML document.
        """
        text = ""
        in_tag = False
        for c in self.body:
            if c == "<":
                in_tag = True
                # Parse 'text' (which in this case is a sequence of characters outside a tag) as a 'Text' node
                if text:
                    self.parse_raw_text(html.unescape(text))
                text = ""
            elif c == ">":
                in_tag = False
                # Parse 'text' as a tag and its contents
                self.parse_tag(text)
                text = ""
            else:
                text += c
        """
        At the end of the loop, this dumps any accumulated text as a Text object.
        Otherwise, if you never saw an angle bracket, you’d return an empty list
        of tokens (This allows you to parse an HTML document that doesn't contain
        any tags as a basic document with text). But unfinished tags,
        like in Hi!<hr, are thrown out.
        """
        if not in_tag and text:
            self.parse_raw_text(text)

        html_tree = self.finish()
        logger.debug(stringify_tree(html_tree))
        return html_tree

    def parse_raw_text(self, text: str):
        """
        A 'Text' node is appended as a child of the last unfinished (i.e. not closed) node.
        """
        # Skip whitespace-only text nodes
        if text.isspace():
            return

        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def parse_tag(self, tag_contents: str):
        """
        tag_contents: a string containing all the text between and '<' and '>'.

        Example:
           Raw HTML tag: <div style="font:normal;">
           tag_contents: div style="font:normal;"
        """
        tag, attributes = self.get_attributes(tag_contents)
        # Throw away the '<!doctype html>' tag and comments
        if tag.startswith("!"):
            return
        # A close tag removes an unfinished node, and adds it to the next unfinished node
        if tag.startswith("/"):
            # Handle the special case of the last tag (which will not have unfinished nodes added to it)
            if len(self.unfinished) == 1:
                return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        # Auto-close special tags
        elif tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        # An open tag adds an unfinished node to the end of the list
        else:
            # Handle the special case of the first tag (which doesn't have a parent)
            if len(self.unfinished) == 0:
                parent = None
            else:
                parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    def get_attributes(self, text: str):
        # todo fix parsing tags and attributes
        """
        Since 'text.split()' seperates by whitespace, we get the wrong result when parsing

        text = 'span style="background-color: orange;"'
        # Results in
        parts = ['span', 'style="background-color:', 'orange;"']
        # But the desired result is
        parts = ['span', 'style="background-color: orange;"']

        Style declarations are seperated by a semicolon.
        """

        # parts = text.split()

        # Pattern to match spaces outside quotes
        pattern = r'\s+(?=([^"]*"[^"]*")*[^"]*$)'
        # Split the string using the pattern
        parts = re.split(pattern, text)

        tag = parts[0].lower()
        attributes = {}
        for attr_pair in parts[1:]:
            # ? Why does the regex pattern return some 'None' values?
            if attr_pair is None:
                continue
            # An unquoted attribute, where an equal sign separates the two
            if "=" in attr_pair:
                key, value = attr_pair.split("=", 1)
                # Strip the quotes from quoted attributes
                if len(value) > 2 and value[0] in ["'", '"']:
                    value = value[1:-1]

                attributes[key.lower()] = value
            # Attributes with omitted values '<input disabled>'
            else:
                attributes[attr_pair.lower()] = ""
        return tag, attributes

    def finish(self):
        if len(self.unfinished) == 0:
            self.parse_tag("html")
        # Turn the incomplete three into a complete tree by closing unfinished nodes
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()


if __name__ == "__main__":
    with open("./examples/parse.html", "r") as file:
        text = file.read()

    nodes = HTMLParser(text).parse()
    print_tree(nodes)
