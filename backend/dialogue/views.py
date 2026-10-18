from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import dialogue_exception_handler
from .serializers import DialogueMessageSerializer
from .services import generate_reply


class DialogueAPIView(APIView):
    """Public JSON endpoints for the local MVP."""

    authentication_classes = []
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    throttle_classes = []
    parser_classes = [JSONParser]

    def get_exception_handler(self):
        return dialogue_exception_handler


class HealthView(DialogueAPIView):
    """Report API reachability without checking external services."""

    def get(self, request):
        return Response({'status': 'ok'})


class DialogueMessageView(DialogueAPIView):
    def post(self, request):
        serializer = DialogueMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        reply = generate_reply(**data)
        return Response({'npc_id': data['npc_id'], 'reply': reply})
