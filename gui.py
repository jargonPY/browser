import sys
import tkinter
import tkinter.font
from browser_layout.layout import get_font
from browser_tab import Tab


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

    def handle_down(self, event) -> None:
        self.tabs[self.active_tab].scroll_down()
        self.draw()

    def handle_click(self, event) -> None:
        """
        When the user clicks on the browser chrome (the if branch), the browser handles it directly, but clicking on
        the page content (the else branch) are still forwarded to the active tab, subtracting CHROME_PX to fix up the coordinates.
        """
        if event.y < self.CHROME_PX:
            if 40 <= event.x < 40 + 80 * len(self.tabs) and 0 <= event.y < 40:
                self.active_tab = int((event.x - 40) / 80)
            # Handle "add new tab" button
            elif 10 <= event.x < 30 and 10 <= event.y < 30:
                # self.load_url("https://browser.engineering/")
                self.load_file("./examples/parse.html")
            # Handle "go back" button
            elif 10 <= event.x < 35 and 50 <= event.y < 90:
                self.tabs[self.active_tab].go_back()
        else:
            self.tabs[self.active_tab].click(event.x, event.y - self.CHROME_PX)
        self.draw()

    def draw(self) -> None:
        """
        Each tab will be 80 pixels wide and 40 pixels tall. We’ll label each tab something like “Tab 4”
        so we don’t have to deal with long tab titles overlapping. And let’s leave 40 pixels on the left
        for a button that adds a new tab. Then, the ith tab starts at
        x position 40 + 80*i and ends at 120 + 80*i.
        """
        # ? Is it no longer necessary to erase from the canvas?
        # self.canvas.delete("all")
        self.tabs[self.active_tab].draw(self.canvas)

        # Sometimes there will be halves of letters that stick out (especially when scrolling) into the browser chrome, but we can hide them by just drawing over them.
        self.canvas.create_rectangle(0, 0, self.WIDTH, self.CHROME_PX, fill="white", outline="black")

        tab_font = get_font(20, "normal", "roman")
        for i, tab in enumerate(self.tabs):
            tab_name = f"Tab {i}"
            tab_start_position_x, tab_end_position_x = 40 + 80 * i, 120 + 80 * i
            tab_start_position_y, tab_end_position_y = 0, 40

            # Draw vertical borders on the left and right and then draw the tab name
            self.canvas.create_line(
                tab_start_position_x, tab_start_position_y, tab_start_position_x, tab_end_position_y, fill="black"
            )
            self.canvas.create_line(
                tab_end_position_x, tab_start_position_y, tab_end_position_x, tab_end_position_y, fill="black"
            )
            self.canvas.create_text(
                tab_start_position_x + 10, 10, anchor="nw", text=tab_name, font=tab_font, fill="black"
            )

            # Draw horizontal border under all tabs except the selected, to help the the user identify which tab is the active tab
            if i == self.active_tab:
                self.canvas.create_line(0, tab_end_position_y, tab_start_position_x, tab_end_position_y, fill="black")
                self.canvas.create_line(
                    tab_end_position_x, tab_end_position_y, self.WIDTH, tab_end_position_y, fill="black"
                )

            # Draw a button for creating new tabs
            button_font = get_font(30, "normal", "roman")
            self.canvas.create_rectangle(10, 10, 30, 30, outline="black", width=1)
            self.canvas.create_text(11, 0, anchor="nw", text="+", font=button_font, fill="black")

            # Draw an address bar
            self.canvas.create_rectangle(40, 50, self.WIDTH - 10, 90, outline="black", width=1)
            url = self.tabs[self.active_tab].url
            self.canvas.create_text(55, 55, anchor="nw", text=url, font=button_font, fill="black")

            # Draw a back button
            self.canvas.create_rectangle(10, 50, 35, 90, outline="black", width=1)
            self.canvas.create_polygon(15, 70, 30, 55, 30, 85, fill="black")

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
