# backend/video_engine/__init__.py
from .adapters.okru import resolve_okru
from .adapters.dailymotion import resolve_dailymotion
from .adapters.streamwish import resolve_streamwish
from .adapters.flickr import resolve_flickr
from .adapters.shortlink import bypass_shortlink

__all__ = [
    "resolve_okru",
    "resolve_dailymotion",
    "resolve_streamwish",
    "resolve_flickr",
    "bypass_shortlink",
]
