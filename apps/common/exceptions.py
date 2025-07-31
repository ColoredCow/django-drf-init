from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is not None:
        message = "Something went wrong"
        code = "UNKNOWN"

        if isinstance(exc, ValidationError):
            message = "Validation failed"
            code = "VALIDATION_ERROR"
        elif isinstance(exc, NotAuthenticated):
            message = "Authentication required"
            code = "AUTH_REQUIRED"

        custom_payload = {
            "status": "error",
            "message": message,
            "data": None,
            "error": {
                "code": code,
                "details": response.data,
            },
        }

        wrapped_response = Response(custom_payload, status=response.status_code)

        # Avoid copying problematic headers
        HEADER_BLACKLIST = {
            "Content-Length",
            "Content-Encoding",
            "Transfer-Encoding",
            "Content-Type",
        }

        for key, value in response.headers.items():
            if key.lower() not in HEADER_BLACKLIST:
                wrapped_response[key] = value

        return wrapped_response

    return response
