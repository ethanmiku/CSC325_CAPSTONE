from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import dialogue_exception_handler
from .history import get_history_messages, save_exchange
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
        scope = {'game_session_id': data['game_session_id'], 'npc_id': data['npc_id']}
        history = get_history_messages(**scope)
        reply = generate_reply(data['npc_id'], data['message'], history)
        save_exchange(**scope, player_message=data['message'], npc_reply=reply)
        return Response({'npc_id': data['npc_id'], 'reply': reply})
