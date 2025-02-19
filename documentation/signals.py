import json

from django.db.models.signals import post_save
from django.dispatch import receiver

from nestmed import settings
from .models import Transcript
import boto3


@receiver(post_save, sender=Transcript)
def send_sns_message(sender, instance, created, **kwargs):
    if created:
        sns_client = boto3.client('sns')
        topic_arn = settings.TRANSCRIPTS_TOPIC
        message = {
            'transcript_id': instance.id,
            'status': 'processing',
            'text': instance.text
        }
        sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            Subject='New Transcript for Processing'
        )
