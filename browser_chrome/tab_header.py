from typing import Tuple, TYPE_CHECKING
import tkinter
import tkinter.font
from browser_config import WINDOW_WIDTH
from browser_layout.layout import get_font

if TYPE_CHECKING:
    from browser_tab import Tab


class TabHeader:
    """
    Each tab will be 80 pixels wide and 40 pixels tall. We’ll label each tab something like “Tab 4”
    so we don’t have to deal with long tab titles overlapping. And let’s leave 40 pixels on the left
    for a button that adds a new tab. Then, the ith tab starts at
    x position 40 + 80*i and ends at 120 + 80*i.
    """

    def __init__(self) -> None:
        self.tab_width = 80
        self.tab_height = 40
        self.offset_x = 40
        self.offset_y = 0
        self.number_of_tabs = 0

    def _compute_x_coordinates(self, tab_index: int) -> Tuple[int, int]:
        x_start = self.offset_x + (self.tab_width * tab_index)
        x_end = (self.offset_x + self.tab_width) + self.tab_width * tab_index
        return x_start, x_end

    def _compute_y_coordinates(self) -> Tuple[int, int]:
        return self.offset_y, self.tab_height

    def is_clicked(self, x_click, y_click) -> bool:
        tabs_end_x = self.offset_x + self.tab_width * self.number_of_tabs

        if self.offset_x <= x_click < tabs_end_x and self.offset_y <= y_click < self.tab_height:
            return True

        return False

    def draw(self, canvas: tkinter.Canvas, tabs: list["Tab"], active_tab: int) -> None:
        self.number_of_tabs = len(tabs)
        tab_font = get_font(20, "normal", "roman")

        for i, tab in enumerate(tabs):
            tab_name = f"Tab {i}"
            tab_start_position_x, tab_end_position_x = self._compute_x_coordinates(i)
            tab_start_position_y, tab_end_position_y = self._compute_y_coordinates()

            # Draw vertical borders on the left and right and then draw the tab name
            canvas.create_line(
                tab_start_position_x, tab_start_position_y, tab_start_position_x, tab_end_position_y, fill="black"
            )
            canvas.create_line(
                tab_end_position_x, tab_start_position_y, tab_end_position_x, tab_end_position_y, fill="black"
            )
            canvas.create_text(tab_start_position_x + 10, 10, anchor="nw", text=tab_name, font=tab_font, fill="black")

            # Draw horizontal border under all tabs except the selected, to help the the user identify which tab is the active tab
            if i == active_tab:
                canvas.create_line(0, tab_end_position_y, tab_start_position_x, tab_end_position_y, fill="black")
                canvas.create_line(
                    tab_end_position_x, tab_end_position_y, WINDOW_WIDTH, tab_end_position_y, fill="black"
                )
