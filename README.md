# `head-context`

Easily manage your assets in meta tags (scripts, css, preload etc.) from anywhere
in the template code (and outside).

## Why

Imagine a form widget, which requires a heavy image processing library that we want to include ONLY IF the widget itself was rendered. Thanks to `head-context` you can specify what resources you need locally (in template fragments, widgets and so on) yet load them in the `head` section of your page with ease.

## What does it do?

```html+jinja
<!doctype html>
<html>
<head>
    <title>My Title!</title>
    <!-- this is where we want all our js/css rendered to be rendered -->
    {{ meta_placeholder() }}
</head>
<body>
    {% include "my-cool-component.html" %}
</body>
</html>
```

And `my-cool-component.html`:

```html+jinja
<!-- we can call these from anywhere and they will be automatically rendered in the right place! -->
{% do push_js('/static/cool-component.js', mode="async") %}
{% do push_css('/static/cool-component.css') %}
{% do push_preload('/static/some-image-we-need.png', 'image') %}
<div class="my-cool-component">
    <!-- ... --->
</div>
```

And that's pretty much it. You can `push_js`/`push_css`/`push_preload` from anywhere in the template (and even outside of templates) and it will be automatically attached to the page being rendered.

## Features

* Supports scripts, styles and preload directives
* Works with Jinja2
* Can be used outside of templates too
  * if you want to render a custom (form) widget for example

## Installation and setup

Simply install `head-context` package:

```bash
pip install head-context
# or with poetry
poetry add head-context
```

Add extension to the Jinja2 environment:

```python

from jinja2 import Environment

env = Environment()
env.add_extension("head_context.jinja_ext.HeadContextExtension")
```

and that's it! From now on you can use `push_css()`/`push_js()`/`push_preload()` and `head_placeholder()`.
