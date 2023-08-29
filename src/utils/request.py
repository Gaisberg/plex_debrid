'''Requests wrapper'''
import json
import requests
from utils.logger import logger

def get(url: str, timeout=5, additional_headers=None) -> json:
    '''Requests get wrapper'''
    session = requests.Session()
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    if additional_headers:
        headers.update(additional_headers)
    response = session.get(url, headers=headers, timeout=timeout)
    return _handle_response(response)

def post(url, data: dict, timeout=5, additional_headers=None) -> json:
    '''Requests post wrapper'''
    session = requests.Session()
    response = session.post(url, headers=additional_headers, data=data, timeout=timeout)
    return _handle_response(response)

def _handle_response(response: requests.Response) -> json:
    if not response.ok:
        logger.warning("Error: %s %s", response.status_code, response.content)
        response = None
    elif len(response.content) > 0:
        response = json.loads(response.content)
    return response
