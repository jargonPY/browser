import socket
import ssl
import json
from loguru import logger


def resolve_url(relative_url: str, host_url: str) -> str:
    """
    Converts a relative URL into a full URL.
    """
    # Full URL
    if "://" in relative_url:
        return relative_url
    # A host-relative URL, reuses the same scheme and host, starts with a '/'
    elif relative_url.startswith("/"):
        scheme, hostpath = host_url.split("://", 1)
        host, old_path = hostpath.split("/", 1)
        return scheme + "://" + host + relative_url
    # A path-relative URL
    else:
        dir, _ = host_url.rsplit("/", 1)
        while relative_url.startswith("../"):
            relative_url = relative_url[3:]
            if dir.count("/") == 2:
                continue
            dir, _ = dir.rsplit("/", 1)
        return dir + "/" + relative_url


def parse_url(url: str):
    logger.debug(f"Provided Url: {url}")

    if not url.startswith("http"):
        if not url.startswith("www."):
            url = "http://www." + url
        else:
            url = "http://" + url

    scheme, url = url.split("://", 1)

    # Scheme://Hostname:Port/Path
    assert scheme in ["http", "https"], f"Browser only supports the HTTP and HTTPS protocols, received {url}."

    # Handle http://www.google.com/index.html
    if url.count("/") > 0:
        host, path = url.split("/", 1)
        path = "/" + path
    # Handle http://www.google.com
    else:
        host = url
        path = "/"

    # Encrypted HTTP connections usually use port 443 instead of port 80
    port = 80 if scheme == "http" else 443

    # Handle custom ports
    if ":" in host:
        host, custom_port = host.split(":", 1)
        port = int(custom_port)

    logger.debug(f"Url: {url}, Scheme: {scheme}, Host: {host}, Port: {port}, Path: {path}")
    return scheme, host, port, path


def request(url: str):
    """
    Url structure:
        Scheme://Hostname:Port/Path
        http://example.org:8080/index.html
    """
    scheme, host, port, path = parse_url(url)

    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
    s.connect((host, port))

    if scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)

    message = "GET {} HTTP/1.0\r\n".format(path).encode("utf8") + "Host: {}\r\n\r\n".format(host).encode("utf8")
    s.send(message)

    # todo 'encoding' should depend on the headers in the response
    response = s.makefile("r", encoding="utf8", newline="\r\n")

    # Parse the status line
    status_line = response.readline()
    version, status, explanation = status_line.split(" ", 2)
    assert status == "200", "{}: {}".format(status, explanation)

    # Parse the headers line by line
    headers = {}
    while True:
        line = response.readline()
        if line == "\r\n":
            break

        header, value = line.split(":", 1)
        headers[header.lower()] = value.strip()

    logger.debug(f"\nHeaders: {json.dumps(headers, indent=4)}\n")

    assert "transfer-encoding" not in headers
    assert "content-encoding" not in headers

    body = response.read()
    s.close()

    logger.debug(f"\nBody: {body}\n")

    return headers, body
