# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Kyle Hultman <kyle@gremlin.com>, Gremlin Inc <sales@gremlin.com>

import json
import logging

from gremlinapi.exceptions import (
    ProxyError,
    ClientError,
    HTTPTimeout,
    HTTPError,
    HTTPBadHeader
)

from gremlinapi.config import GremlinAPIConfig

try:
    import requests
    import requests.adapters
except ImportError:
    requests = None

log = logging.getLogger('GremlinAPI.client')


class GremlinAPIHttpClient(object):
    @classmethod
    def api_call(cls, method, uri, *args, **kwargs):
        error_message = f'This function is not implemented, please consume the proper http library for your environment'
        log.fatal(error_message)
        raise NotImplementedError(error_message)

    @classmethod
    def header(cls, *args, **kwargs):
        api_key = kwargs.get('api_key', GremlinAPIConfig.api_key)
        bearer_token = kwargs.get('bearer_token', GremlinAPIConfig.bearer_token)
        header = dict()
        if api_key and not bearer_token:
            header['Authorization'] = 'Key {api_key}'
        if bearer_token:
            if "Bearer" in bearer_token:
                header['Authorization'] = bearer_token
            else:
                header['Authorization'] = f'Bearer {bearer_token}'
        else:
            error_msg = f'Missing API Key or Bearer Token, none supplied: {api_key}, {bearer_token}'
            log.fatal(error_msg)
            raise HTTPBadHeader(error_msg)
        return header





class GremlineAPIRequestsClient(GremlinAPIHttpClient):
    @classmethod
    def api_call(cls, method, endpoint, *args, **kwargs):

        request_methods = {
            "HEAD": requests.head,
            "GET": requests.get,
            "POST": requests.post,
            "PUT": requests.put,
            "DELETE": requests.delete,
            "PATCH": requests.patch,
        }

        uri = f'{GremlinAPIConfig.base_uri}{endpoint}'
        client = request_methods.get(method.upper())
        raw_content = kwargs.pop("raw_content", False)
        data = None
        if 'data' in kwargs:
            data = kwargs.pop('data')
        elif 'body' in kwargs:
            if "Content-Type" not in kwargs["headers"]:
                kwargs["headers"]["Content-Type"] = "application/json"
            data = json.dumps(kwargs.pop("body"))

        if data:
            resp = client(uri, data=data, **kwargs)
        else:
            resp = client(uri, **kwargs)

        if raw_content:
            body = resp.content
        else:
            try:
                body = resp.json()
            except ValueError:
                # No JSON in response
                body = str(resp.content, resp.encoding)

        if resp.status_code >= 400:
            log.debug(f'{client}\n{uri}\n{data}\n{kwargs}')
            raise HTTPError(resp, body)
        return resp, body


class GremlinAPIurllibClient(GremlinAPIHttpClient):
    @classmethod
    def api_call(cls, method, uri, *args, **kwargs):
        error_message = f'This function is not yet implemented'
        log.fatal(error_message)
        raise NotImplementedError(error_message)


def get_gremlin_httpclient():
    if requests:
        return GremlineAPIRequestsClient
    else:
        return GremlinAPIurllibClient
