import sys
import tkinter
import tkinter.font
from typing import Literal
from utils.fonts_cache import get_font
from browser_tab import Tab
from browser_chrome.back_button import BackButton
from browser_chrome.address_bar import AddressBar
from browser_chrome.new_tab_button import NewTabButton
from browser_chrome.tab_header import TabHeader


class Browser:
    WIDTH, HEIGHT = 800, 600
    H_STEP, V_STEP = 13, 18
    SCROLL_STEP = 100
    # Reserved space for the browser chrome
    CHROME_PX = 100

    def __init__(self) -> None:
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=self.WIDTH, height=self.HEIGHT, bg="white")
        self.canvas.pack()
        self.window.bind("<Up>", self.handle_up)
        self.window.bind("<Down>", self.handle_down)
        self.window.bind("<Button-1>", self.handle_click)
        self.window.bind("<Key>", self.handle_key)
        self.window.bind("<Return>", self.handle_enter)
        self.window.bind("<BackSpace>", self.handle_backspace)
        self.window.bind("<Control-v>", self.handle_paste)
        self.window.bind("<Command-v>", self.handle_paste)

        self.tabs: list[Tab] = []
        self.active_tab: int = 0

        self.tab_header = TabHeader()
        self.address_bar = AddressBar()
        self.new_tab_button = NewTabButton()
        self.back_button = BackButton()

        self.focus: Literal["address bar"] | None = None
        self.address_bar_value = ""

    def handle_paste(self, event: tkinter.Event):
        if self.focus == "address bar":
            self.address_bar_value = self.window.clipboard_get()
            self.draw()

    def handle_backspace(self, event: tkinter.Event):
        if self.focus == "address bar":
            self.address_bar_value = self.address_bar_value[:-1]
            self.draw()

    def handle_enter(self, event: tkinter.Event):
        if self.focus == "address bar":
            self.tabs[self.active_tab].load_url(self.address_bar_value)
            self.focus = None
            self.draw()

    def handle_key(self, event: tkinter.Event):
        if len(event.char) == 0:
            return

        # Ignore characters that represent a non-character key (below 0x20) or are outside the ASCII range (above 0x7F)
        if not (0x20 <= ord(event.char) < 0x7F):
            return

        if self.focus == "address bar":
            self.address_bar_value += event.char
            self.draw()

    def handle_up(self, event: tkinter.Event) -> None:
        self.tabs[self.active_tab].scroll_up()
        self.draw()

    def handle_down(self, event: tkinter.Event) -> None:
        self.tabs[self.active_tab].scroll_down()
        self.draw()

    def handle_click(self, event: tkinter.Event) -> None:
        """
        When the user clicks on the browser chrome (the if branch), the browser handles it directly, but clicking on
        the page content (the else branch) are still forwarded to the active tab, subtracting CHROME_PX to fix up the coordinates.
        """
        # Clicking outside of an element, clears the focus
        self.focus = None

        if event.y < self.CHROME_PX:
            if self.tab_header.is_clicked(event.x, event.y):
                self.active_tab = int((event.x - self.tab_header.offset_x) / self.tab_header.tab_width)

            elif self.new_tab_button.is_clicked(event.x, event.y):
                # self.load_url("https://browser.engineering/")
                self.load_file("./examples/parse.html")

            elif self.back_button.is_clicked(event.x, event.y):
                self.tabs[self.active_tab].go_back()

            elif 50 <= event.x < self.address_bar.end_x_pos - 10 and 50 <= event.y < 90:
                self.focus = "address bar"
                self.address_bar_value = ""
        else:
            self.tabs[self.active_tab].click(event.x, event.y - self.CHROME_PX)
        self.draw()

    def draw(self) -> None:
        # self.canvas.delete("all")
        active_tab = self.tabs[self.active_tab]
        button_font = get_font(30, "normal", "roman")

        active_tab.draw(self.canvas)

        # Sometimes there will be halves of letters that stick out (especially when scrolling) into the browser chrome, but we can hide them by just drawing over them.
        self.canvas.create_rectangle(0, 0, self.WIDTH, self.CHROME_PX, fill="white", outline="black")

        self.new_tab_button.draw(self.canvas, button_font)
        self.tab_header.draw(self.canvas, self.tabs, self.active_tab)
        self.back_button.draw(self.canvas)

        if self.focus == "address bar":
            self.address_bar.draw(self.canvas, self.address_bar_value, self.focus, self.address_bar_value, button_font)
            w = button_font.measure(self.address_bar_value)
            self.canvas.create_line(55 + w, 55, 55 + w, 85, fill="black")
        else:
            self.address_bar.draw(self.canvas, active_tab.url, self.focus, self.address_bar_value, button_font)

    def load_url(self, url: str) -> None:
        new_tab = Tab()
        new_tab.load_url(url)
        self.active_tab = len(self.tabs)
        self.tabs.append(new_tab)
        self.draw()

    def load_file(self, file_name: str) -> None:
        new_tab = Tab()
        new_tab.load_file(file_name)
        self.active_tab = len(self.tabs)
        self.tabs.append(new_tab)
        self.draw()


# http://example.org/index.html

# http://browser.engineering/text.html


if __name__ == "__main__":
    url = sys.argv[1]
    # Browser().load_url(url)
    Browser().load_file("./examples/parse.html")
    tkinter.mainloop()
