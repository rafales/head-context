from functools import partial
from typing import Callable, Iterable, TypeAlias, Any

from jinja2 import Environment
from jinja2.compiler import generate
from jinja2.ext import Extension
from markupsafe import Markup

from .context import HeadContext, head_context, push_js, push_css, push_preload
from .utils import SafeHTML

ConcatFn: TypeAlias = Callable[[Iterable[str]], str]


class HeadContextExtension(Extension):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        environment.concat = partial(self.concat, environment.concat)  # type: ignore
        environment.globals.update(**self.get_globals())

    def concat(self, wrapped: ConcatFn, value: Iterable[str]) -> str:
        # setup new rendering context if none is present
        token = None
        if (ctx := head_context.get()) is None:
            token = head_context.set(ctx := HeadContext())

        try:
            rendered = wrapped(value)
        finally:
            # restore old rendering context
            if token is not None:
                head_context.reset(token)

        if ctx.replacement_token in rendered:
            # replace the token with the actual media headers
            rendered = rendered.replace(ctx.replacement_token, ctx.render_media())
        elif token is not None and not ctx.is_empty():
            # if we started context at this point and couldn't render JS/CSS
            # then there is something wrong.
            raise RuntimeError(
                f"JS/CSS files were never rendered (render_media() call missing?). "
            )

        return rendered

    def get_globals(self) -> dict[str, Any]:
        return {
            "head_placeholder": self.head_placeholder,
            "push_js": push_js,
            "push_css": push_css,
            "push_preload": push_preload,
        }

    def head_placeholder(self) -> SafeHTML:
        if not (ctx := head_context.get()):
            raise RuntimeError("No meta context found")

        return Markup(ctx.replacement_token)

    def parse(self, parser):
        # parse should never be called because we didn't specify any tags to be parsed,
        # but PyCharm complains about not implementing it, so here it is.
        raise RuntimeError("Shouldn't be called because no 'tags' attribute is defined")


def preview_template(env: Environment, name: str) -> str:
    """
    Return a preview of the python code generated for given template.

    This is mostly a helper for debugging.

    :param env: jinja environment to render the template with
    :param name: full name of the template, e.g. "myapp/detail.html"
    :returns: python code as a string
    """
    assert env.loader is not None, "env.loader must be set"

    source, filename, uptodate = env.loader.get_source(env, name)
    parsed = env._parse(source, name, filename)
    result = generate(parsed, env, name, filename)
    # this shouldn't happen really unless we pass in "stream" parameter
    assert (
        result is not None
    ), "generate() did not return a string, something went wrong"
    return result
