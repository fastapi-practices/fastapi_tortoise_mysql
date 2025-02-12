#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from msgspec import json
from starlette.responses import JSONResponse


class MsgSpecJSONResponse(JSONResponse):
    """
    JSON response using the high-performance msgspec library to serialize data to JSON.
    """

    def render(self, content: Any) -> bytes:
        return json.encode(content)
