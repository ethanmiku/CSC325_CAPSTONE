from django.db import models


class GameProgress(models.Model):
    current_day = models.PositiveIntegerField(default=1)
    clue_found = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)