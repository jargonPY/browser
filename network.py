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
        scheme, host_path = host_url.split("://", 1)
        host, old_path = host_path.split("/", 1)
        return scheme + "://" + host + relative_url
    # A path-relative URL
    else:
        directory, _ = host_url.split("/", 1)
        while relative_url.startswith("../"):
            relative_url = relative_url[3:]
            if directory.count("/") == 2:
                continue
        return directory + "/" + relative_url


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
