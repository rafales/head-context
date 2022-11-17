import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import cached_property
from typing import Literal, Optional, TypeAlias, Sequence, Any

from typing_extensions import Protocol

from head_context.utils import html_params, SafeHTML

CrossOrigin: TypeAlias = Literal["anonymous", "use-credentials"] | bool
Integrity: TypeAlias = str | Sequence[str] | None
PreloadAs: TypeAlias = Literal[
    "audio",
    "document",
    "embed",
    "fetch",
    "font",
    "image",
    "object",
    "script",
    "style",
    "track",
    "worker",
    "video",
]


class AnyAsset(SafeHTML, Protocol):
    pass


@dataclass()
class Preload:
    """
    Specifies a resource which will need to be loaded very soon and
    instructs the browser to start fetching it right away.

    Basically uses `<link rel="preload">` tag.
    """

    #: URL to the resource
    href: str
    #: What kind of resource are we dealing here with, passed to "as"
    as_: PreloadAs
    content_type: Optional[str] = None
    #: if the attached link should issue a cross-origin request or not
    crossorigin: CrossOrigin = field(default=False, kw_only=True)
    integrity: Integrity = field(default=None, kw_only=True)

    def get_html_params(self) -> dict[str, Any]:
        return {
            "rel": "preload",
            "as": self.as_,
            "href": self.href,
            "type": self.content_type,
            "crossorigin": self.crossorigin,
            "integrity": self.integrity,
        }

    def __html__(self) -> str:
        return f"<link {html_params(**self.get_html_params())}>"


@dataclass()
class JsAsset:
    """
    Specifies a JavaScript asset to be attached to the rendered page via `<script>` tag.
    """

    src: str
    crossorigin: CrossOrigin = field(default=False, kw_only=True)
    integrity: Integrity = field(default=None, kw_only=True)
    mode: None | Literal["defer", "async"] = field(default=None, kw_only=True)

    def get_html_params(self) -> dict[str, Any]:
        return {
            "src": self.src,
            "crossorigin": self.crossorigin,
            "integrity": self.integrity,
            "defer": self.mode == "defer",
            "async": self.mode == "async",
        }

    def __html__(self) -> str:
        return f"<script {html_params(**self.get_html_params())}></script>"


@dataclass()
class CssAsset:
    """
    Specifies a css asset to be attached to the rendered page via <link> tag.
    """

    href: str
    crossorigin: CrossOrigin = field(default=False, kw_only=True)
    integrity: Integrity = field(default=None, kw_only=True)

    def get_html_params(self) -> dict[str, Any]:
        return {
            "rel": "stylesheet",
            "href": self.href,
            "crossorigin": self.crossorigin,
            "integrity": self.integrity,
        }

    def __html__(self) -> str:
        return f"<link {html_params(**self.get_html_params())}>"


@dataclass
class HeadContext:
    assets: list[AnyAsset] = field(default_factory=list)

    # this is needed to embed a random token in the generated template,
    # so we can replace it with the actual JS/CSS headers. See `MediaExtension`.
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def push_asset(self, asset: AnyAsset) -> None:
        if asset not in self.assets:
            self.assets.append(asset)

    @cached_property
    def replacement_token(self) -> str:
        return f"<!-- MEDIA_SLOT:{self.id} -->"

    def is_empty(self) -> bool:
        return not self.assets

    def render_media(self) -> str:
        return "\n".join(asset.__html__() for asset in self.assets)


head_context = ContextVar[HeadContext | None]("head_context", default=None)


def push_js(src: str, **kwargs) -> None:
    ctx = head_context.get()
    if ctx is None:
        raise RuntimeError("No context")
    ctx.push_asset(JsAsset(src=src, **kwargs))


def push_css(href: str, **kwargs) -> None:
    ctx = head_context.get()
    if ctx is None:
        raise RuntimeError("No context")
    ctx.push_asset(CssAsset(href=href, **kwargs))


def push_preload(href: str, as_: PreloadAs, **kwargs) -> None:
    ctx = head_context.get()
    if ctx is None:
        raise RuntimeError("No context")
    ctx.push_asset(Preload(href=href, as_=as_, **kwargs))
