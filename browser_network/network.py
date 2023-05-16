import socket


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


def request(url: str):
    """
    Url structure:
        Scheme://Hostname:Port/Path
        http://example.org:8080/index.html
    """
    if url.startswith("https://"):
        url = url.replace("https", "http")

    if not url.startswith("http"):
        if not url.startswith("www."):
            url = "http://www." + url
        else:
            url = "http://" + url

    # Scheme://Hostname:Port/Path
    assert url.startswith("http://"), f"Browser only supports the HTTP protocol, received {url}."
    url = url[len("http://") :]  # Remove the http portion

    # Handle http://www.google.com/index.html
    if url.count("/") > 2:
        host, path = url.split("/", 1)
        path = "/" + path
    # Handle http://www.google.com
    else:
        host = url
        path = "/"

    port = 80

    # Handle custom ports
    if ":" in host:
        host, custom_port = host.split(":", 1)
        port = int(custom_port)

    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
    s.connect((host, port))

    message = "GET {} HTTP/1.0\r\n".format(path).encode("utf8") + "Host: {}\r\n\r\n".format(host).encode("utf8")
    s.send(message)

    response = s.makefile("r", encoding="iso-8859-1", newline="\r\n")

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

    for key, item in headers.items():
        print("KEY: ", key, " ITEM: ", item)

    assert "transfer-encoding" not in headers
    assert "content-encoding" not in headers

    body = response.read()
    s.close()

    return headers, body
