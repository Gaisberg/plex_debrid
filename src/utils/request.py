"""Requests wrapper"""
import json
import requests
import xmltodict
from utils.logger import logger


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
        data = {}
        if len(response.content) > 0:
            if "text/xml" in response.headers.get("Content-Type"):
                data = xmltodict.parse(response.content)
            elif "application/json" in response.headers.get("Content-Type"):
                data = json.loads(response.content)
            else:
                data = response.content
        return data


def get(url: str, timeout=10, additional_headers=None) -> ResponseObject:
    """Requests get wrapper"""
    session = requests.Session()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if additional_headers:
        headers.update(additional_headers)
    try:
        response = session.get(url, headers=headers, timeout=timeout)
    except:
        pass
    return ResponseObject(response)


def post(url, data: dict, timeout=10, additional_headers=None) -> ResponseObject:
    """Requests post wrapper"""
    session = requests.Session()
    try:
        response = session.post(
            url, headers=additional_headers, data=data, timeout=timeout
        )
    except:
        pass
    return ResponseObject(response)


def put(url, data: dict = None, timeout=10, additional_headers=None) -> ResponseObject:
    """Requests put wrapper"""
    session = requests.Session()
    try:
        response = session.put(
            url, data=data, headers=additional_headers, timeout=timeout
        )
    except:
        pass
    return ResponseObject(response)
