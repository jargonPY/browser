from abc import ABC, abstractmethod
import tkinter.font

"""
Conceptually, the display list contains commands.
"""


class DrawCommand(ABC):
    def __init__(self, x1: float, y1: float) -> None:
        self.top = x1
        self.bottom = y1

    @abstractmethod
    def execute(self, scroll: float, canvas: tkinter.Canvas) -> None:
        pass


class DrawText(DrawCommand):
    def __init__(self, x1: float, y1: float, text: str, font: tkinter.font.Font, color: str) -> None:
        self.left = x1
        self.top = y1
        self.text = text
        self.font = font
        self.color = color
        # A field used by the browser's 'draw' method to skip offscreen graphics
        self.bottom = y1 + font.metrics("linespace")

    def execute(self, scroll, canvas) -> None:
        """
        Passing the 'scroll' amount as a parameter allows each graphics command to do
        the necessary coordinate conversion itself.
        """
        canvas.create_text(self.left, self.top - scroll, text=self.text, font=self.font, fill=self.color, anchor="nw")


# Backgrounds are rectangles
class DrawRect(DrawCommand):
    def __init__(self, x1: float, y1: float, x2: float, y2: float, color: str) -> None:
        self.left = x1
        self.top = y1
        self.right = x2
        self.bottom = y2
        self.color = color

    def execute(self, scroll, canvas) -> None:
        canvas.create_rectangle(
            self.left,
            self.top - scroll,
            self.right,
            self.bottom - scroll,
            width=0,
            fill=self.color,
        )
