from django.db import models
import string
import random


def generate_unique_code():
    lenght = 8
    while True:
        code = "".join(random.choices(string.ascii_uppercase, k=lenght))
        if Room.objects.filter(code=code).count() == 0:
            break

    return code


class Room(models.Model):
    code = models.CharField(max_length=10, default=generate_unique_code, blank=True)
    host = models.CharField(max_length=100, unique=True)
    guest_can_pause = models.BooleanField(null=False, default=True)
    votes_to_skip = models.IntegerField(null=False, default=1)
    created_at = models.TimeField(auto_now_add=True)
