import pytest
from browser_css.css_parser import CSSParser
from browser_css.css_selectors import *


def test_word():
    text = """
    body {
        color: red;
    }
    """

    result = CSSParser(text).word()

    assert result == "body"


def test_property_value_pair():
    text = "color: red;"
    result = CSSParser(text).property_value_pair()
    assert result == ("color", "red")

    text = "background-color:white;"
    result = CSSParser(text).property_value_pair()
    assert result == ("background-color", "white")

    text = "background-color : white;"
    result = CSSParser(text).property_value_pair()
    assert result == ("background-color", "white")


def test_parse_body():
    text = """
            color: red;
            background-color: white;
            """

    result = CSSParser(text).parse_body()

    assert result == {"color": "red", "background-color": "white"}


def test_parse_body_with_invalid_property():
    text = """
            @**!color: red;
            background-color: white;
            """

    result = CSSParser(text).parse_body()

    assert result == {"background-color": "white"}


def test_parse_body_with_invalid_value():
    text = """
            color: red;
            background-color: @**!white;
            """

    result = CSSParser(text).parse_body()

    assert result == {"color": "red"}


def test_tag_selector():
    text = """
    body {
        color: red;
        background-color: white;
    }
    """

    result = CSSParser(text).parse_css_file()

    assert result == [(TagSelector("body"), {"color": "red", "background-color": "white"})]


def test_class_selector():
    text = """
    .main {
        color: red;
        background-color: white;
    }
    """

    result = CSSParser(text).parse_css_file()

    class_selector = (ClassSelector("main"), {"color": "red", "background-color": "white"})
    assert result == [class_selector]


def test_id_selector():
    text = """
    #main {
        color: red;
        background-color: white;
    }
    """

    result = CSSParser(text).parse_css_file()

    id_selector = (IdSelector("main"), {"color": "red", "background-color": "white"})
    assert result == [id_selector]


def test_list_selector_with_two_tags():
    text = """
    div, p {
        color: red;
        background-color: white;
    }
    """

    result = CSSParser(text).parse_css_file()

    list_selector = (ListSelector(["div", "p"]), {"color": "red", "background-color": "white"})
    assert result == [list_selector]


def test_list_selector_with_four_tags():
    text = """
    div, h1, h2, p {
        color: red;
        background-color: white;
    }
    """

    result = CSSParser(text).parse_css_file()

    list_selector = (ListSelector(["div", "h1", "h2", "p"]), {"color": "red", "background-color": "white"})
    assert result == [list_selector]


def test_descendant_selector_tag_selector_follwed_by_another_tag_selector():
    text = """
    div p {
        color: red;
        background-color: white;
    }
    """

    result = CSSParser(text).parse_css_file()

    ancestor = TagSelector("div")
    descendant = TagSelector("p")
    descendant_selector = (DescendantSelector(ancestor, descendant), {"color": "red", "background-color": "white"})
    assert result == [descendant_selector]


def test_descendant_selector_tag_selector_follwed_by_class_selector():
    text = """
    div .container {
        color: red;
        background-color: white;
    }
    """

    result = CSSParser(text).parse_css_file()

    ancestor = TagSelector("div")
    descendant = ClassSelector("container")
    descendant_selector = (DescendantSelector(ancestor, descendant), {"color": "red", "background-color": "white"})
    assert result == [descendant_selector]


def test_descendant_selector_with_several_descendants():
    text = """
    div .container p .title {
        color: red;
        background-color: white;
    }
    """

    result = CSSParser(text).parse_css_file()

    ancestor = TagSelector("div")
    descendant = ClassSelector("container")
    descendant_selector = DescendantSelector(ancestor, descendant)

    descendant = TagSelector("p")
    descendant_selector = DescendantSelector(descendant_selector, descendant)

    descendant = ClassSelector("title")
    descendant_selector = (
        DescendantSelector(descendant_selector, descendant),
        {"color": "red", "background-color": "white"},
    )

    assert result == [descendant_selector]


def test_multiple_tag_selectors():
    text = """
    body {
        color: red;
        background-color: white;
    }

    p {
        color: green;
    }
    """

    result = CSSParser(text).parse_css_file()

    body_selector = (TagSelector("body"), {"color": "red", "background-color": "white"})
    p_selector = (TagSelector("p"), {"color": "green"})
    assert result == [body_selector, p_selector]


def test_invalid_selector_followed_by_valid_selector():
    text = """
    @body {
        color: red;
        background-color: white;
    }

    h1 < h2 {
        color: red;
    }

    p {
        color: green;
    }
    """

    result = CSSParser(text).parse_css_file()

    p_selector = (TagSelector("p"), {"color": "green"})
    assert result == [p_selector]


# def test_parse_period():
#     text = """
#     @media (prefers-color-scheme: light) {
#         body {
#             color:#333;
#         }
#     }

#     a:link { color: #04a; }

#     pre, code { hyphens: none; -webkit-hyphens: none; }

#     html { font-size: 24px; line-height: 1.3; padding: 0.5ex; }

#     h1:not(.title):hover{ cursor: pointer; text-decoration: underline }

#     .main header * { margin: 0; }


#     @media print {
#         html { font-size: 12px; }
#         #signup, nav.links { display: none;}
#         .note-container:before { content: " ["; }
#         .note-container, .note-container:before, .note-container:after { color: navy; }
#         pre { font-size: 0.8333rem; }
#         #toc a { text-decoration: none; color: black; }
#     }

#     code .st { color: #888; }
#     """

#     result = CSSParser(text).parse_css_file()
#     print("\nRESULT: ", result)

#     p_selector = (TagSelector("html"), {"font-size": "24px", "line-height": "1.3", "padding": "0.5ex"})
#     ancestor = TagSelector("code")
#     descendant = ClassSelector("st")
#     descendant_selector = (DescendantSelector(ancestor, descendant), {"color": "#888"})
#     assert result == [p_selector, descendant_selector]


"""
 html { font-size: 24px; line-height: 1.3; padding: 0.5ex; }
body {
    max-width: 65ex; margin: 0 auto; font-family: 'Lora', 'Times', sans-serif;
    text-align: justify; hyphens: auto; -webkit-hyphens: auto;
}
@media (prefers-color-scheme: light) {
body {
    color:#333;
}
}
@media (max-width: 800px) {
    html { font-size: 18px; }
}

pre, code { hyphens: none; -webkit-hyphens: none; }
pre { font-size: 18px; overflow: auto; padding-left: 2ex; }

dt { margin-top: 1em; }
dd { margin-bottom: 1em; }

abbr { font-variant: small-caps; font-weight: bold; }

blockquote { border-left: 1ex solid #eee; padding-left: 1ex; margin-left: 0; }

footer { text-align: center; font: italic 60% serif; margin: 5em 0; }

header, h1, strong { font-family: 'Vollkorn', 'Garamond', serif;}
@media (prefers-color-scheme: light) {
header, h1, strong {
    color:black;
}
}
h1 { font-size: 105%; margin: 1.5em 0 0; }
header { text-align: center; margin: 3em 0 1em; }
header h1 { font-size: 200%; font-weight: bold; }
h1:not(.title):hover{ cursor: pointer; text-decoration: underline }
.main header * { margin: 0; }
header .author { font-style: italic; }
header .author:before { content: "By "; }

@media (prefers-color-scheme: light) {
a:link { color: #04a; }
a:hover { color: #08f; }
a:visited { color: #84a; }
a:visited:hover { color: #c4f; }
a:active { color: #f64; }
}

li { margin: 1em 0; }

.main ol, .main > h1 { font-size: 120%; }
.main header { margin-bottom: 3em; }
.main > h1 { margin: 0; }
.main ol { margin: 0; padding-left: 0}
@media (prefers-color-scheme: light) {
.main ol { color: black; }
}
.main li { font-size: 80%; font-style: italic; }
.main li a, .main li .link { font-size: 125%; font-style: normal; }
#onepage { font-size: 125% }
.intro, .outro { }
.intro ol { list-style: lower-roman; }
.outro ol { list-style: upper-alpha; }

nav.links {
    line-height: 40px; text-align: center;
    border-radius: 10px; background: #eee;
    padding: 0 40px; position: relative; margin-bottom: 3em;
}
@media (prefers-color-scheme: dark) {
nav.links {
    background: #333;
}
}
nav.links ~ nav.links { margin-top: 3em; }
@media (prefers-color-scheme: light) {
nav.links {
    color: black;
}
nav.links a {
    color: black;
}
}
nav.links a[rel] {
    display: block; width: 40px; height: 100%; position: absolute; top: 0;
    font-size: 36px; text-decoration: none; cursor: pointer;
}
nav.links a[rel]:hover { background: #ddd; }
@media (prefers-color-scheme: light) {
nav.links a[rel]:hover { background: #222; }    
}

nav.links a[rel=prev] {
    left: 0; border-radius: 10px 0 0 10px; border-right: 3px solid white;
}
nav.links a[rel=next] {
    right: 0; border-radius: 0 10px 10px 0; border-left: 3px solid white;
}

#toc:before {
    content: "Table of Contents"; display: block; text-align: center;
    font-size: 105%; font-weight: bold; background-color: #eee;
    font-family: 'Vollkorn', 'Garamond', serif; color: black; 
}
@media (prefers-color-scheme: dark) {
#toc:before {
    color:white;
    background-color:#333;
}
}
div#toc { border: 2px solid #eee; border-radius: 10px; }
div#toc:before { padding: .5em 0; border-radius: 10px 10px 0 0; }

nav#toc {
    float: right; width: 25ex; clear: right; margin: 0 -28ex 1em 0;
    font-size: 60%; border-bottom: 2px solid #eee;
}
nav#toc:before { padding: 1ex; }
nav#toc ul { list-style: none; padding: 0; }

nav#toc { display: none; }
@media only screen and (min-width: 1150px) {
    div#toc { display: none; }
    nav#toc { display: block; }
}
.main nav#toc { display: none; }

body { counter-reset: fn; }
.note-container { counter-increment: fn; white-space: pre; cursor: pointer; }
.note-container:after { content: "]"; }
.note-container:before { content: " [" counter(fn); }
.note-container.open:before { content: " ["; }
.note { font-style: italic; white-space: normal; }
.note em { font-style: normal; }
@media (prefers-color-scheme: light) {
.note-container:after, .note-container:before, .note { color: #a86; }
}
}
/* Assume no footnotes on main page, but margin numbers */
body.main { padding: 0 4ex; }
@media only screen and (min-width: 1150px) {
    body { width: 65ex; padding: 0 17ex 0 0; }
    .note {
        float: right; width: 25ex; clear: right; margin: 0 -28ex 1em 0;
        font-size: 110%; vertical-align: reset; text-align: left;
    }
    div .note { margin-right: calc(-28ex - 1rem - 2px); }
    .note-container { font-size: 60%; vertical-align: super; cursor: auto; }
    .note-container.open:before { content: "Â [" counter(fn); color: #a86; }
    .note:before { content: counter(fn) ". "; }
}
@media (prefers-color-scheme: light) ) {
.note {
    color: black;
}
}
@media only screen and (min-width: 1350px) {
    body { padding: 0 17ex; }
}
@media only screen and (max-width: 1149px) {
  .note-container .note { display: none; }
  .open .note { display: inline; }
  .note form { display: inline; }
}

.todo, .quirk, .warning, .installation, .further, .demo { padding: 1em 1em 0; margin: 1em 0; }
.quirk:before, .warning:before, .installation:before {
    font-weight: bold; font-family: 'Vollkorn', 'Garamond', serif;
    text-align: center;
}

figure { text-align: center; }
.grid figure { margin: .5em; }
figure img { width: 100%; }

.quirk { border: 2px solid purple; }
.quirk:before { content: "Quirk"; color: purple; }
.warning { border: 2px solid red; }
.warning:before { content: "Warning"; color: red; }
.installation { border: 2px solid blue; }
.installation:before { content: "Installation"; color: blue; }
.demo { border: 2px solid gray; }
.demo:before { content: "Demonstration"; color: gray; }
.further { border: 2px solid green; padding-top: 0; }
.further > :first-child:before { content: "Go further: "; font-weight: bold; color: green; }
.widget { width: 100%; border: 2px solid navy; }

@media (prefers-color-scheme: dark) {
.quirk { border: 2px solid #CBC3E3; }
.quirk:before { color: #CBC3E3; }
.warning { border: 2px solid #FFCCCB; }
.warning:before { color: #FFCCCB; }
.installation { border: 2px solid lightblue; }
.installation:before { color: lightblue; }
.further { border: 2px solid lightgreen; }
.further > :first-child:before { color: lightgreen; }
.widget { width: 100%; border: 2px solid navy; }
}

code .st { color: #666; }
code .cf { color: #606; }
code .kw { color: #606; }
code .im { color: #606; }
code .co { color: #a86; }

@media (prefers-color-scheme: dark) {
code .st { color: #aaa; }
code .cf { color: #a0a; }
code .kw { color: #a0a; }
code .im { color: #a0a; }
code .co { color: #C4A484; }
}

.todo { background: darkred; color: white; padding-bottom: 1em; }
.todo:before { content: "This book is a work in progress:"; }
@media (prefers-color-scheme: dark) {
.todo {
    background: lightred;
    color:black;
}
}
input[type=checkbox][disabled] { display: none; }

#overlay {
    position: fixed; top: 0; right: 0; bottom: 0; left: 0;
    background-color: rgba(256, 256, 256, .9);
    overflow:auto;
}
.popup {
    padding: 1em; border: 1px solid gray; box-shadow: 0 0 20px 10px gray;
    width: 50ex; margin: 3em auto; background: white;
}
@media (prefers-color-scheme: dark) {
#overlay {
    background-color: rgba(0, 0, 0, .9);
}
.popup {
    background: black;
}
}
.popup h1 { text-align: center; }
.popup .inputs { font-size: 30px; }
.popup .inputs label { font-size: 24px; }
.popup input { font-size: 30px; width: 400px; }
.popup .legalese { font-size: 60%; }
.popup button { font-size: 24px; }

.popup textarea { width: 500px; height: 250px; }

.confirm-feedback { display: none; }
.confirm-feedback.active { display: block; }

p, li, div.sourceCode, .note { position: relative; }
.tools {
    position: absolute; right: 0; top: -1.5em; background: #eee;
    padding: .125em .75em; border-radius: .75em;
}
.tools a { margin: 0 1ex; }
@media only screen and (min-width: 1150px) {
    .feedback.note { font-size: 66%; }
}
.feedback.note { color: purple; }
.feedback.note span { outline: none; }
.feedback.note form { margin-top: .5ex; }
@media (prefers-color-scheme: dark) {
.tools {
    background: #333;
}
.feedback.note { color: #CBC3E3; }
}

form { overflow: auto; }
input, button { font-size: inherit; font-family: inherit; }
form h1 { margin-bottom: 1em; margin-top: 0; }
.field { display: flex; }
.field label { min-width: 15ex; vertical-align: bottom; }
.field input { flex-grow: 1; min-width: 0; }
.checkoff { float: right; }
.checkoff input { vertical-align: middle; }
a.checkoff { font-size: 24px; }
form .checkoff, form button[type=submit] { margin-top: 1em; }

#signup { border: 2px solid gold; position: relative; text-align: center; }
#signup-close {
    position: absolute; top: 0; right: 8px;
    font-size: 0; text-decoration: none; color: #333;
}
#signup-close:hover { color: #f64; }
#signup-close:active { color: red; }
#signup-close::before { font-size: 24px; content: "âï¸"; }

.outline { font-size: 60%; font-family: monospace; column-width: 30ch; }
.outline code { break-inside: avoid; display: block; }
.outline > code { margin: .33em 0; }
.outline code > code { margin-left: 2ch; }

@media print {
    html { font-size: 12px; }
    #signup, nav.links { display: none;}
    .note-container:before { content: " ["; }
    .note-container, .note-container:before, .note-container:after { color: navy; }
    pre { font-size: 0.8333rem; }
    #toc a { text-decoration: none; color: black; }
}

.highlight-region { font-size: 24px; line-height: 1.5; padding: 1em; }
.highlight-region mark { position: relative; padding: .1em; }
.highlight-region label {
    position: absolute; font: bold 80% sans-serif; 
}
"""
