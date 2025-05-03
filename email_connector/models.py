from django.db import models
from django.contrib.auth.models import User

class GmailAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_uri = models.TextField(default='https://oauth2.googleapis.com/token')
    client_id = models.TextField()
    client_secret = models.TextField()
    token_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email
