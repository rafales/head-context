from jinja2 import Environment, PackageLoader

from head_context.context import JsAsset, CssAsset


def test_basic_rendering() -> None:
    env = Environment(autoescape=True, loader=PackageLoader("tests", "templates"))
    env.add_extension("head_context.jinja_ext.MediaExtension")

    tpl = env.get_template("test/base.html")
    tpl.render()


def test_injecting_works() -> None:
    env = Environment(autoescape=True, loader=PackageLoader("tests", "templates"))
    env.add_extension("head_context.jinja_ext.MediaExtension")

    tpl = env.from_string(
        """
    {% extends "test/base.html" %}
    {% block body %}
    {{ push_js("/static/test.js") }}
    {{ push_css("/static/test.css") }}
    {{ push_preload("/static/test.png", "image") }}
    {% endblock %}
    """
    )
    output = tpl.render()
    assert "/static/test.js" in output
    assert "/static/test.css" in output
    assert "/static/test.png" in output


def test_js_rendering() -> None:
    js = JsAsset("/static/test.js")
    assert js.__html__() == '<script src="/static/test.js"></script>'

    js = JsAsset("/static/test.js", mode="defer")
    assert js.__html__() == '<script defer src="/static/test.js"></script>'

    js = JsAsset("/static/test.js", mode="async")
    assert js.__html__() == '<script async src="/static/test.js"></script>'

    js = JsAsset("/static/test.js", crossorigin="anonymous")
    assert (
        js.__html__()
        == '<script crossorigin="anonymous" src="/static/test.js"></script>'
    )

    js = JsAsset("/static/test.js", crossorigin=True)
    assert js.__html__() == '<script crossorigin src="/static/test.js"></script>'

    js = JsAsset("/static/test.js", integrity="sha256-...")
    assert (
        js.__html__()
        == '<script integrity="sha256-..." src="/static/test.js"></script>'
    )


def test_css_rendering() -> None:
    css = CssAsset("/static/test.css")
    assert css.__html__() == '<link href="/static/test.css" rel="stylesheet">'

    css = CssAsset("/static/test.css", crossorigin="anonymous")
    assert (
        css.__html__()
        == '<link crossorigin="anonymous" href="/static/test.css" rel="stylesheet">'
    )

    css = CssAsset("/static/test.css", crossorigin=True)
    assert (
        css.__html__() == '<link crossorigin href="/static/test.css" rel="stylesheet">'
    )

    css = CssAsset("/static/test.css", integrity="sha256-...")
    assert (
        css.__html__()
        == '<link href="/static/test.css" integrity="sha256-..." rel="stylesheet">'
    )


def test_asset_deduplication() -> None:
    env = Environment(autoescape=True, loader=PackageLoader("tests", "templates"))
    env.add_extension("head_context.jinja_ext.MediaExtension")

    tpl = env.from_string(
        """
    {% extends "test/base.html" %}
    {% block body %}
    {{ push_js("/static/test.js") }}
    {{ push_js("/static/test.js") }}
    {% endblock %}
    """
    )
    output = tpl.render()
    assert output.count("/static/test.js") == 1
