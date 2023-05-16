import tkinter
import tkinter.font


class BackButton:
    def __init__(self) -> None:
        self.start_x_pos = 10
        self.end_x_pos = 35
        self.start_y_pos = 50
        self.end_y_pos = 90

    def is_clicked(self, x_click, y_click) -> bool:
        if self.start_x_pos <= x_click < self.end_x_pos and self.start_y_pos <= y_click < self.end_y_pos:
            return True

        return False

    def draw(self, canvas: tkinter.Canvas) -> None:
        canvas.create_rectangle(
            self.start_x_pos, self.start_y_pos, self.end_x_pos, self.end_y_pos, outline="black", width=1
        )
        canvas.create_polygon(15, 70, 30, 55, 30, 85, fill="black")
