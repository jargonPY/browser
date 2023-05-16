import tkinter
import tkinter.font
from draw_commands import DrawCommand
from browser_config import WINDOW_WIDTH


class AddressBar:
    def __init__(self) -> None:
        self.start_x_pos = 40
        self.end_x_pos = WINDOW_WIDTH - 10
        self.start_y_pos = 50
        self.end_y_pos = 90

        self.text_x_pos = 55
        self.text_y_pos = 55

    def draw(self, canvas: tkinter.Canvas, url: str | None, font) -> None:
        canvas.create_rectangle(
            self.start_x_pos, self.start_y_pos, self.end_x_pos, self.end_y_pos, outline="black", width=1
        )
        canvas.create_text(self.text_x_pos, self.text_y_pos, anchor="nw", text=url, font=font, fill="black")
