from rest_framework import status as drf_status
from rest_framework.response import Response


def success_response(data=None, message="Success", status=drf_status.HTTP_200_OK):
    return Response(
        {
            "status": "success",
            "message": message,
            "data": data,
            "error": None,
        },
        status=status,
    )


def error_response(message="Error", error=None, status=drf_status.HTTP_400_BAD_REQUEST):
    return Response(
        {
            "status": "error",
            "message": message,
            "data": None,
            "error": error or {},
        },
        status=status,
    )
