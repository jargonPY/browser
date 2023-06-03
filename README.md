# browser

This repository contains a Python implementation of a basic browser described in the great book [Browser Engineering](https://browser.engineering/).

This implementation extends the original browser to support:

- A more complete implementation of the [box model](https://developer.mozilla.org/en-US/docs/Learn/CSS/Building_blocks/The_box_model), to support margins and padding.

- A more complete implementation of the layout of block-level and inline-level elements as described by the [visual formatting model](https://www.w3.org/TR/CSS2/visuren.html).

- Added support for additional CSS selectors.

### Using the browser

```
// Provide the website to load
python gui.py http://browser.engineering/text.html
```

Once the browser is started you can navigate to other websites by typing directly into the the address bar.
