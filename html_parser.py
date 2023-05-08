from abc import ABC
from typing import List, Union


class Node(ABC):
    def __init__(self, parent: Union["Node", None]) -> None:
        self.parent = parent
        self.children: List[Node] = []


class Text(Node):
    def __init__(self, text: str, parent: Node | None) -> None:
        self.text = text
        # todo conver to 'super(parent)' call to initialize 'parent' and 'children'
        self.parent = parent
        # Even though 'Text' nodes never have children, this is added for consistency, to avoid 'isinstance' calls throughout the code
        self.children: List[Node] = []

    def __repr__(self) -> str:
        return repr(self.text)


class Element(Node):
    def __init__(self, tag: str, attributes: List[str], parent: Node | None) -> None:
        self.tag = tag
        self.attributes = attributes
        self.parent = parent
        self.children: List[Node] = []

    def __repr__(self) -> str:
        return f"< {self.tag} >"


def print_tree(node: Node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)


class HTMLParser:
    SELF_CLOSING_TAGS = [
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    ]

    def __init__(self, body: str) -> None:
        self.body = body
        self.unfinished: List[Node] = []

    def parse(self):
        text = ""
        in_tag = False
        for c in self.body:
            if c == "<":
                in_tag = True
                if text:
                    self.add_text(text)
                text = ""
            elif c == ">":
                in_tag = False
                self.add_tag(text)
                text = ""
            else:
                text += c
        """
        At the end of the loop, this dumps any accumulated text as a Text object.
        Otherwise, if you never saw an angle bracket, you’d return an empty list
        of tokens. But unfinished tags, like in Hi!<hr, are thrown out.
        """
        if not in_tag and text:
            self.add_text(text)
        return self.finish()

    def add_text(self, text: str):
        """
        A 'Text' node is appended as a child of the last unfinished (not closed) node.
        """
        # Skip whitespace-only text nodes
        if text.isspace():
            return

        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tag(self, tag: str):
        tag, attributes = self.get_attributes(tag)
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
        elif tag in HTMLParser.SELF_CLOSING_TAGS:
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
        parts = text.split()
        tag = parts[0].lower()
        attributes = {}
        for attr_pair in parts[1:]:
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
            self.add_tag("html")
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
