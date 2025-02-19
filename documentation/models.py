from django.db import models


class Transcript(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    audio_file = models.FileField(upload_to='audio/', null=True)

    def __str__(self):
        return f"Transcript {self.id} - {self.created_at}"
