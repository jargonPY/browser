from typing import Tuple, Dict
import tkinter.font
from browser_css.css_selectors import Selector

# relative_x, word, font, color
TextInLine = Tuple[float, str, tkinter.font.Font, str]

# x, y, word, font, color
TextStyle = Tuple[float, float, str, tkinter.font.Font, str]

CSSPropertyName = str
CSSPropertyValue = str
CSSProperties = Dict[CSSPropertyName, CSSPropertyValue]
CSSRule = Tuple[Selector, CSSProperties]
