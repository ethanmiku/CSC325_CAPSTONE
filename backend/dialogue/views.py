from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Report API reachability without checking external services."""

    authentication_classes = []
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    throttle_classes = []

    def get(self, request):
        return Response({'status': 'ok'})

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if isinstance(exc, MethodNotAllowed):
            response.data = {
                'error': {
                    'code': 'method_not_allowed',
                    'message': str(exc.detail),
                }
            }
        return response
