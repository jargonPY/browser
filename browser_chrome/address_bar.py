import tkinter
import tkinter.font
from browser_config import WINDOW_WIDTH


class AddressBar:
    def __init__(self) -> None:
        self.start_x_pos = 40
        self.end_x_pos = WINDOW_WIDTH - 10
        self.start_y_pos = 50
        self.end_y_pos = 90

        self.text_x_pos = 55
        self.text_y_pos = 55

    def draw(self, canvas: tkinter.Canvas, url: str | None, focus, address_bar_value: str, font) -> None:
        canvas.create_rectangle(
            self.start_x_pos, self.start_y_pos, self.end_x_pos, self.end_y_pos, outline="black", width=1
        )

        if focus == "address bar":
            canvas.create_text(
                self.text_x_pos, self.text_y_pos, anchor="nw", text=address_bar_value, font=font, fill="black"
            )
            w = font.measure(address_bar_value)
            canvas.create_line(55 + w, 55, 55 + w, 85, fill="black")
        else:
            canvas.create_text(self.text_x_pos, self.text_y_pos, anchor="nw", text=url, font=font, fill="black")
