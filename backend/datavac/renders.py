from typing import Any

import orjson
from rest_framework.renderers import JSONRenderer


class ORJSONRenderer(JSONRenderer):
    """Fast ORJSON renderer for Django Rest Framework."""

    media_type = 'application/json'
    format = 'json'

    def render(
        self, data: Any, accepted_media_type: str | None = None, renderer_context: dict[str, Any] | None = None
    ) -> bytes:
        # orjson.OPT_SERIALIZE_DATACLASS allows serialization of dataclasses
        # orjson.OPT_UTC_ZONINFO formats dates with timezones
        if data is None:
            return b''
        return orjson.dumps(data, option=orjson.OPT_SERIALIZE_DATACLASS | orjson.OPT_UTC_Z)
