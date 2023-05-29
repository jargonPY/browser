import tkinter
import tkinter.font
from browser_layout.layout import Layout
from browser_layout.document_layout import DocumentLayout
from browser_html.html_parser import HTMLParser, Node, Element
from draw_commands import DrawCommand
from browser_css.css_parser import CSSParser
from browser_css.css_rules import sort_rules_by_priority, add_css_to_html_node
from browser_network.network import request, resolve_url
from utils.utils import tree_to_list
from browser_html.html_nodes import Text
from browser_config import WINDOW_HEIGHT, SCROLL_STEP, CHROME_PX
from utils.utils import stringify_tree
from loguru import logger

# todo find another solution for dealing with potetial 'None' state (
# * maybe intialize Tab in a valid state, although a tab without a url is a valid state)
# * another option is to not define the state in the '__init__' method, the downside of that is that is obscures which properties a class has


class Tab:
    def __init__(self) -> None:
        self.scroll = 0
        self.url: str | None = None
        self.history: list[str] = []
        self.display_list: list[DrawCommand] = []

        with open("./browser_css/browser_defaults.css", "r") as file:
            file_content = file.read()
            self.default_style_sheet = CSSParser(file_content).parse_css_file()
            # ? Is this a good way of setting the default styles to the lowest priority
            for selector, body in self.default_style_sheet:
                selector.priority = 1

    def scroll_up(self) -> None:
        self.scroll = max(self.scroll - SCROLL_STEP, 0)

    def scroll_down(self) -> None:
        # Use the total page height to avoid scrolling past the bottom of the page
        max_y = self.layout_tree.block_height - (WINDOW_HEIGHT - CHROME_PX)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)

    def go_back(self) -> None:
        if len(self.history) > 1:
            # Remove current url from the list
            self.history.pop()
            # Remove previous url from the list
            previous_url = self.history.pop()
            self.load(previous_url)

    def click(self, x_coordinate: int, y_coordinate: int) -> None:
        """
        The event x and y coordinates are relative to the browser window. Since the canvas is in
        the top-left corner of the window, those are also the x and y coordinates relative to the
        canvas. We want the coordinates relative to the web page, so we need to account for scrolling.
        """

        click_x, click_y = x_coordinate, y_coordinate + self.scroll

        # Figure out which elements are at that location
        objs: list[Layout] = []
        for obj in tree_to_list(self.layout_tree, []):
            within_block_width = obj.abs_x <= click_x < obj.abs_x + obj.block_width
            within_block_height = obj.abs_y < click_y < obj.abs_y + obj.block_height
            if within_block_width and within_block_height:
                objs.append(obj)

        if not obj:
            return

        # When clicking on some text, you’re also clicking on the paragraph it’s in, and the section that that paragraph is in, and so on.
        # We want the most specific node which is the last object in the list.
        html_element: Node | None = objs[-1].node
        # For a link node, the most specific node that was clicked (i.e. element) is a text node.
        # But since we want to know the actual URL the user clicked on, we need to climb back up the HTML tree to find the link element.
        while html_element:
            if isinstance(html_element, Text):
                pass
            elif isinstance(html_element, Element) and html_element.tag == "a" and "href" in html_element.attributes:
                # todo find another solution for dealing with potetial 'None' state (maybe intialize Tab in a valid state, although a tab without a url is a valid state)
                assert self.url is not None, "Tried to access url when url is not set"

                url = resolve_url(html_element.attributes["href"], self.url)
                # Clear the current layout tree when fetching a new resource
                self.display_list = []
                return self.load_url(url)
            html_element = html_element.parent

    def draw(self, canvas: tkinter.Canvas):
        canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + WINDOW_HEIGHT - CHROME_PX:
                continue
            if cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll - CHROME_PX, canvas)

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

        # with open("./examples/parse.css", "r") as file:
        #     file_content = file.read()
        #     rules.extend(CSSParser(file_content).parse_css_file())

        for link in links:
            try:
                # todo find another solution for dealing with potetial 'None' state (maybe intialize Tab in a valid state, although a tab without a url is a valid state)
                assert self.url is not None, "Tried to access url when url is not set"

                header, body = request(resolve_url(link, self.url))
                logger.debug(f"Link: {link}")
                logger.debug(f"\n\n{body}")

            # todo make the exception more sepcific
            except Exception as e:
                logger.exception(e)
                continue

            rules.extend(CSSParser(body).parse_css_file())

        sorted_rules = sort_rules_by_priority(rules)
        add_css_to_html_node(html_tree, sorted_rules)
        logger.debug(stringify_tree(html_tree))

        self.layout_tree = DocumentLayout(html_tree)
        self.layout_tree.layout()
        self.layout_tree.paint(self.display_list)
