import sys
import tkinter
import tkinter.font
from layout import Layout, DocumentLayout
from browser_html.html_parser import HTMLParser, print_tree, Node, Element
from draw_commands import DrawCommand
from browser_css.css_parser import CSSParser
from browser_css.css_rules import cascade_priority, add_css_to_html_node
from network import request, resolve_url
from utils.utils import tree_to_list
from browser_html.html_nodes import Text


class Tab:
    WIDTH, HEIGHT = 800, 600
    H_STEP, V_STEP = 13, 18
    SCROLL_STEP = 100
    # Reserved space for the browser chrome
    CHROME_PX = 100

    def __init__(self) -> None:
        self.scroll = 0
        self.url: str | None = None
        self.history: list[str] = []

        # Since the Tab class is responsible for layout, styling, and painting, the default style sheet moves to the Tab constructor
        with open("./browser_css/browser_defaults.css", "r") as file:
            file_content = file.read()
            self.default_style_sheet = CSSParser(file_content).parse_css_file()

    def scroll_down(self) -> None:
        # self.scroll += self.SCROLL_STEP
        # Use the page height to avoid scrolling past the bottom of the page
        max_y = self.doc_layout.block_height - (self.HEIGHT - self.CHROME_PX)
        self.scroll = min(self.scroll + self.SCROLL_STEP, max_y)

    def click(self, x_coordinate: int, y_coordinate: int) -> None:
        """
        The event x and y coordinates are relative to the browser window. Since the canvas is in
        the top-left corner of the window, those are also the x and y coordinates relative to the
        canvas. We want the coordinates relative to the web page, so we need to account for scrolling.
        """

        click_x, click_y = x_coordinate, y_coordinate + self.scroll

        # Figure out which elements are at that location
        objs = []
        for obj in tree_to_list(self.doc_layout, []):
            within_block_width = obj.abs_x <= click_x < obj.abs_x + obj.block_width
            within_block_height = obj.abs_y < click_y < obj.abs_y + obj.block_height
            if within_block_width and within_block_height:
                objs.append(obj)

        if not obj:
            return

        # When clicking on some text, you’re also clicking on the paragraph it’s in, and the section that that paragraph is in, and so on.
        # We want the one that’s “on top”, which is the last object in the list.

        # This is the most specific node that was clicked
        element = objs[-1].node
        # For a link node, the most specific node that was clicked (i.e. element) is a text node.
        # But since we want to know the actual URL the user clicked on, we need to climb back up the HTML tree to find the link element.
        while element:
            if isinstance(element, Text):
                pass
            elif element.tag == "a" and "href" in element.attributes:
                url = resolve_url(element.attributes["href"], self.url)
                return self.load_url(url)
            element = element.parent

    def draw(self, canvas: tkinter.Canvas):
        for cmd in self.display_list:
            if cmd.top > self.scroll + self.HEIGHT - self.CHROME_PX:
                continue
            if cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll - self.CHROME_PX, canvas)

    def go_back(self) -> None:
        if len(self.history) > 1:
            # Remove current url from the list
            self.history.pop()
            # Remove previous url from the list
            previous_url = self.history.pop()
            self.load(previous_url)

    def load_url(self, url: str):
        self.url = url
        self.history.append(url)
        headers, body = request(url)
        self.load(body)

    def load_file(self, file_name: str) -> None:
        self.url = file_name
        with open(file_name, "r") as file:
            raw_html = file.read()
        self.load(raw_html)

    def load(self, raw_html: str):
        html_tree = HTMLParser(raw_html).parse()

        # ? Why do a shallow copy of the list?
        rules = self.default_style_sheet.copy()

        links = [
            node.attributes["href"]
            for node in tree_to_list(html_tree, [])
            if isinstance(node, Element)
            and node.tag == "link"
            and "href" in node.attributes
            and node.attributes.get("rel") == "stylesheet"
        ]

        for link in links:
            try:
                header, body = request(resolve_url(link, self.url))
            # todo make the exception more sepcific
            except:
                continue
            rules.extend(CSSParser(body).parse_css_file())

        """
        Before sorting rules, it is in file order. Since Python’s sorted function keeps the
        relative order of things when possible, file order thus acts as a tie breaker, as it should.
        """
        sorted_rules = sorted(rules, key=cascade_priority)
        add_css_to_html_node(html_tree, sorted_rules)

        self.doc_layout = DocumentLayout(html_tree)
        self.doc_layout.layout()
        self.display_list = []
        self.doc_layout.paint(self.display_list)
        # self.display_list = self.doc_layout.display_list
