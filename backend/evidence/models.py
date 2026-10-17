from django.db import models

# Create your models here.

class Clue(models.Model):
    # Unique identifier for each clue
    clue_id = models.CharField(max_length=50, unique=True)

    # Name of the clue
    name = models.CharField(max_length=100)

    # Description shown when examining the clue
    description = models.TextField()

    # Location where the clue can be found
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name