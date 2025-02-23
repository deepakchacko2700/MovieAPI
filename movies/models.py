from django.db import models
from django.contrib.auth.models import User
import uuid


class Collection(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(User, related_name='collections', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Movie(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    genres = models.CharField(max_length=200, null=True, blank=True)
    collection = models.ForeignKey(Collection, related_name='movies', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_genres_list(self):
        return [genre.strip() for genre in self.genres.split(',')]