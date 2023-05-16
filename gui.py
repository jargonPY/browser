import sys
import tkinter
import tkinter.font
from browser_layout.layout import get_font
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
        self.window.bind("<Down>", self.handle_down)
        self.window.bind("<Button-1>", self.handle_click)

        self.tabs: list[Tab] = []
        self.active_tab: int = 0

        self.tab_header = TabHeader()
        self.address_bar = AddressBar()
        self.new_tab_button = NewTabButton()
        self.back_button = BackButton()

    def handle_down(self, event: tkinter.Event) -> None:
        self.tabs[self.active_tab].scroll_down()
        self.draw()

    def handle_click(self, event: tkinter.Event) -> None:
        """
        When the user clicks on the browser chrome (the if branch), the browser handles it directly, but clicking on
        the page content (the else branch) are still forwarded to the active tab, subtracting CHROME_PX to fix up the coordinates.
        """
        if event.y < self.CHROME_PX:
            if self.tab_header.is_clicked(event.x, event.y):
                self.active_tab = int((event.x - self.tab_header.offset_x) / self.tab_header.tab_width)

            elif self.new_tab_button.is_clicked(event.x, event.y):
                # self.load_url("https://browser.engineering/")
                self.load_file("./examples/parse.html")

            elif self.back_button.is_clicked(event.x, event.y):
                self.tabs[self.active_tab].go_back()
        else:
            self.tabs[self.active_tab].click(event.x, event.y - self.CHROME_PX)
        self.draw()

    def draw(self) -> None:
        active_tab = self.tabs[self.active_tab]
        button_font = get_font(30, "normal", "roman")

        active_tab.draw(self.canvas)

        # Sometimes there will be halves of letters that stick out (especially when scrolling) into the browser chrome, but we can hide them by just drawing over them.
        self.canvas.create_rectangle(0, 0, self.WIDTH, self.CHROME_PX, fill="white", outline="black")

        self.new_tab_button.draw(self.canvas, button_font)
        self.tab_header.draw(self.canvas, self.tabs, self.active_tab)
        self.back_button.draw(self.canvas)
        self.address_bar.draw(self.canvas, active_tab.url, button_font)

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
