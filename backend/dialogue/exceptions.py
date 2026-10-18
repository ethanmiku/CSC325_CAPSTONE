"""Translate REST Framework errors into the documented API envelope."""

import logging

from rest_framework.exceptions import (
    MethodNotAllowed, NotAcceptable, ParseError, UnsupportedMediaType, ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def flatten_errors(value, path=''):
    if isinstance(value, dict):
        result = {}
        for key, child in value.items():
            name = 'body' if key == 'non_field_errors' else str(key)
            result.update(flatten_errors(child, f'{path}.{name}' if path else name))
        return result
    if isinstance(value, list):
        if all(not isinstance(item, (dict, list)) for item in value):
            return {path or 'body': [str(item) for item in value]}
        result = {}
        for index, child in enumerate(value):
            result.update(flatten_errors(child, f'{path}.{index}' if path else str(index)))
        return result
    return {path or 'body': [str(value)]}


def dialogue_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        # Keep exception bodies and player/provider content out of the response/log.
        logger.error('Unexpected dialogue API failure (%s)', type(exc).__name__)
        return Response({'error': {
            'code': 'internal_error',
            'message': 'An unexpected backend error occurred.',
        }}, status=500)

    if isinstance(exc, (ValidationError, ParseError)):
        error = {
            'code': 'invalid_request',
            'message': 'The request contains invalid fields.',
            'details': flatten_errors(response.data),
        }
    else:
        codes = {
            MethodNotAllowed: 'method_not_allowed',
            UnsupportedMediaType: 'unsupported_media_type',
            NotAcceptable: 'not_acceptable',
        }
        code = next((value for cls, value in codes.items() if isinstance(exc, cls)),
                    getattr(exc, 'default_code', 'internal_error'))
        error = {'code': code, 'message': str(getattr(exc, 'detail', 'Request failed.'))}
    response.data = {'error': error}
    return response
