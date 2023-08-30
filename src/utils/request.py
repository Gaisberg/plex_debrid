"""Requests wrapper"""
import json
import requests
import xmltodict
from utils.logger import logger


def get(url: str, timeout=5, additional_headers=None) -> dict:
    """Requests get wrapper"""
    session = requests.Session()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if additional_headers:
        headers.update(additional_headers)
    response = session.get(url, headers=headers, timeout=timeout)
    return _handle_response(response)


def post(url, data: dict, timeout=5, additional_headers=None) -> dict:
    """Requests post wrapper"""
    session = requests.Session()
    response = session.post(url, headers=additional_headers, data=data, timeout=timeout)
    return _handle_response(response)


def put(url, data: dict = None, timeout=5, additional_headers=None) -> dict:
    """Requests put wrapper"""
    session = requests.Session()
    response = session.put(url, data=data, headers=additional_headers, timeout=timeout)
    if not response.ok:
        logger.warning("Error: %s %s", response.status_code, response.content)
    return _handle_response(response)


def _handle_response(response: requests.Response) -> dict:
    if not response.ok:
        logger.warning("Error: %s %s", response.status_code, response.content)
        response = None
    if len(response.content) > 0:
        if "text/xml" in response.headers.get("Content-Type"):
            response = xmltodict.parse(response.content)
        elif "application/json" in response.headers.get("Content-Type"):
            response = json.loads(response.content)
    return response
