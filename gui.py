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


class Browser:
    WIDTH, HEIGHT = 800, 600
    H_STEP, V_STEP = 13, 18
    SCROLL_STEP = 100

    def __init__(self) -> None:
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=self.WIDTH, height=self.HEIGHT, bg="white")
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scroll_down)
        self.times_font = tkinter.font.Font(family="Times New Roman", size=16, weight="bold", slant="italic")

        with open("./browser_css/browser_defaults.css", "r") as file:
            file_content = file.read()
            self.default_style_sheet = CSSParser(file_content).parse_css_file()

    def scroll_down(self, event):
        # self.scroll += self.SCROLL_STEP
        # Use the page height to avoid scrolling past the bottom of the page
        max_y = self.doc_layout.block_height - self.HEIGHT
        self.scroll = min(self.scroll + self.SCROLL_STEP, max_y)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        # for cursor_x, cursor_y, c, font in self.display_list:
        #     # Avoid drawing characters that are outside the viewing window
        #     if cursor_y > self.scroll + self.HEIGHT:
        #         continue

        #     if cursor_y + self.V_STEP < self.scroll:
        #         continue

        #     self.canvas.create_text(cursor_x, cursor_y - self.scroll, text=c, font=font, anchor="nw")
        for cmd in self.display_list:
            if cmd.top > self.scroll + self.HEIGHT:
                continue
            if cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll, self.canvas)

    def load(self, url: str):
        headers, body = request(url)
        html_tree = HTMLParser(body).parse()
        self.doc_layout = DocumentLayout(html_tree)
        self.doc_layout.layout()
        # self.display_list = self.doc_layout.display_list
        self.display_list: list[DrawCommand] = []
        self.doc_layout.paint(self.display_list)
        self.draw()

    def load_local(self, file_name: str):
        with open(file_name, "r") as file:
            html = file.read()

        html_tree = HTMLParser(html).parse()

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
                header, body = request(resolve_url(link, url))
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
        self.draw()


# http://example.org/index.html

# http://browser.engineering/text.html

if __name__ == "__main__":
    url = sys.argv[1]
    # Browser().load(url)
    Browser().load_local("./examples/parse.html")
    tkinter.mainloop()
