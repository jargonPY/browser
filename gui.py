import sys
import socket
import tkinter
import tkinter.font
from layout import Layout, DocumentLayout
from html_parser import HTMLParser, print_tree


class Browser:
    WIDTH, HEIGHT = 800, 600
    H_STEP, V_STEP = 13, 18
    SCROLL_STEP = 100

    def __init__(self) -> None:
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scroll_down)
        self.times_font = tkinter.font.Font(family="Times New Roman", size=16, weight="bold", slant="italic")

    def scroll_down(self, event):
        self.scroll += self.SCROLL_STEP
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for cursor_x, cursor_y, c, font in self.display_list:
            # Avoid drawing characters that are outside the viewing window
            if cursor_y > self.scroll + self.HEIGHT:
                continue

            if cursor_y + self.V_STEP < self.scroll:
                continue

            self.canvas.create_text(cursor_x, cursor_y - self.scroll, text=c, font=font, anchor="nw")

    def load(self, url: str):
        headers, body = request(url)
        html_tree = HTMLParser(body).parse()
        self.doc_layout = DocumentLayout(html_tree)
        self.doc_layout.layout()
        self.display_list = self.doc_layout.display_list
        self.draw()

    def load_local(self, file_name: str):
        with open(file_name, "r") as file:
            html = file.read()
        html_tree = HTMLParser(html).parse()
        self.doc_layout = DocumentLayout(html_tree)
        self.doc_layout.layout()
        self.display_list = self.doc_layout.display_list
        self.draw()


def request(url: str):
    """
    Url structure:
        Scheme://Hostname:Port/Path
        http://example.org:8080/index.html
    """
    # Scheme://Hostname:Port/Path
    assert url.startswith("http://")  # Browser only supports the HTTP protocol
    url = url[len("http://") :]  # Remove the http portion

    host, path = url.split("/", 1)
    path = "/" + path
    port = 80

    # Handle custom ports
    if ":" in host:
        host, custom_port = host.split(":", 1)
        port = int(custom_port)

    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
    s.connect((host, port))

    message = "GET {} HTTP/1.0\r\n".format(path).encode("utf8") + "Host: {}\r\n\r\n".format(host).encode("utf8")
    s.send(message)

    response = s.makefile("r", encoding="utf8", newline="\r\n")

    # Parse the status line
    status_line = response.readline()
    version, status, explanation = status_line.split(" ", 2)
    assert status == "200", "{}: {}".format(status, explanation)

    # Parse the headers
    headers = {}
    while True:
        line = response.readline()
        if line == "\r\n":
            break

        header, value = line.split(":", 1)
        headers[header.lower()] = value.strip()

    assert "transfer-encoding" not in headers
    assert "content-encoding" not in headers

    body = response.read()
    s.close()

    return headers, body


# http://example.org/index.html

# https://browser.engineering/examples/xiyouji.html

# http://browser.engineering/text.html

if __name__ == "__main__":
    url = sys.argv[1]
    # Browser().load(url)
    Browser().load_local("./examples/parse.html")
    tkinter.mainloop()
