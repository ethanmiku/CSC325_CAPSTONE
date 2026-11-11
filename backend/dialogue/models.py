from django.db import models
from django_mongodb_backend.fields import ArrayField


class NPCProfile(models.Model):
    npc_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    personality = models.TextField()
    background = models.TextField()
    known_facts = ArrayField(models.TextField(), default=list, blank=True)

    def __str__(self):
        return self.name


class DialogueExchange(models.Model):
    game_session_id = models.UUIDField()
    npc_id = models.CharField(max_length=100)
    player_message = models.TextField()
    npc_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=['game_session_id', 'npc_id', '-created_at', '-id'],
                name='dialogue_exchange_history_idx',
            ),
        ]
