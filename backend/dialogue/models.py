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
