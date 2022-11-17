# `head-context`

Easily manage your assets in meta tags (scripts, css, preload etc.) from anywhere
in the template code (and outside).

## Why

Imagine a form widget, which requires a heavy image processing library that we want to include ONLY IF the widget itself was rendered. Thanks to `head-context` you can specify what resources you need locally (in template fragments, widgets etc.) yet load them in the `head` section of your page with ease.

## What does it do?

```html+jinja
<!doctype html>
<html>
<head>
    <title>My Title!</title>
    <!-- this is where we want all our js/css files to be rendered -->
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
{% do push_js('/static/cool-component.js') %}
{% do push_css('/static/cool-component.css') %}
<div class="my-cool-component">
    <!-- ... --->
</div>
```

And that's pretty much it. You can `push_js`/`push_css` from anywhere in the template (and even outside of templates) and it will be automatically attached to the page being rendered.

