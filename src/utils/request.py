import json
import xmltodict
import requests
from types import SimpleNamespace
import logging

logger = logging.getLogger(__name__)


class ResponseObject:
    """Response object"""

    def __init__(self, response: requests.Response):
        self.response = response
        self.is_ok = response.ok
        self.data = self.handle_response(response)

    def handle_response(self, response: requests.Response):
        """Handle different types of responses"""
        if not self.is_ok:
            logger.warning("Error: %s %s", response.status_code, response.content)

        if len(response.content) > 0:
            content_type = response.headers.get("Content-Type")
            if "text/xml" in content_type:
                return xmltodict.parse(response.content)
            elif "application/json" in content_type:
                return json.loads(response.content)
            else:
                return response.content
        return {}


def _handle_request_exception() -> SimpleNamespace:
    """Handle exceptions during requests and return a namespace object."""
    logger.error("Request failed", exc_info=True)
    return SimpleNamespace(ok=False, data={}, content={}, status_code=500)


def _make_request(
    method: str, url: str, data: dict = None, timeout=10, additional_headers=None
) -> ResponseObject:
    session = requests.Session()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if additional_headers:
        headers.update(additional_headers)

    try:
        response = session.request(
            method, url, headers=headers, data=data, timeout=timeout
        )
    except requests.RequestException:
        response = _handle_request_exception()

    return ResponseObject(response)


def get(url: str, timeout=10, additional_headers=None) -> ResponseObject:
    """Requests get wrapper"""
    return _make_request(
        "GET", url, timeout=timeout, additional_headers=additional_headers
    )


def post(url: str, data: dict, timeout=10, additional_headers=None) -> ResponseObject:
    """Requests post wrapper"""
    return _make_request(
        "POST", url, data=data, timeout=timeout, additional_headers=additional_headers
    )


def put(
    url: str, data: dict = None, timeout=10, additional_headers=None
) -> ResponseObject:
    """Requests put wrapper"""
    return _make_request(
        "PUT", url, data=data, timeout=timeout, additional_headers=additional_headers
    )
