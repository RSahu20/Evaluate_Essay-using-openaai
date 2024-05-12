# essays/models.py

from django.db import models
from django.contrib.auth.models import User

class Essay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    submission_date = models.DateTimeField(auto_now_add=True)
    feedback_text = models.TextField(blank=True)

