import boto3
import json
import os
import openai
from botocore.exceptions import ClientError

# Initialize clients
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')  # For invoking the TranscriptProcessingFunction
openai.api_key = os.environ['OPEN_API_KEY']


def lambda_handler(event, context):
    # Get the S3 event information
    record = event['Records'][0]
    bucket_name = record['s3']['bucket']['name']
    object_key = record['s3']['object']['key']

    # Check that the file is in the 'audio/' prefix
    if not object_key.startswith('audio/'):
        print(f"Ignoring non-audio file: {object_key}")
        return {
            'statusCode': 200,
            'body': json.dumps('Non-audio file, ignoring...')
        }

    try:
        # Download the audio file from S3
        audio_file_path = '/tmp/' + os.path.basename(object_key)
        s3_client.download_file(bucket_name, object_key, audio_file_path)

        # Process the audio file with OpenAI Whisper for transcription
        with open(audio_file_path, 'rb') as audio_file:
            transcription = openai.Audio.transcribe(model="whisper-1", file=audio_file)

        # Extract the transcribed text
        transcript_text = transcription['text']

        # Retrieve the S3 object tags to get the transcript_id
        response = s3_client.get_object_tagging(Bucket=bucket_name, Key=object_key)
        transcript_id = None
        for tag in response['TagSet']:
            if tag['Key'] == 'transcript_id':
                transcript_id = tag['Value']
                break

        if not transcript_id:
            raise Exception("Transcript ID not found in tags.")

        # Prepare the payload to send to TranscriptProcessingFunction
        payload = {
            'transcript_id': transcript_id,
            'transcript_text': transcript_text
        }

        # Send the transcript to the TranscriptProcessingFunction
        lambda_response = lambda_client.invoke(
            FunctionName=os.environ['TRANSCRIPT_PROCESSING_FUNCTION_ARN'],  # Add your function ARN here
            InvocationType='Event',  # Use 'Event' to invoke asynchronously
            Payload=json.dumps(payload)
        )

        # Log the Lambda response
        print(f"Sent transcription to TranscriptProcessingFunction: {lambda_response}")

        # Create a new key for the transcript output
        transcript_key = object_key.replace('audio/', 'transcripts/') + '.txt'

        # Save the transcription result to the S3 bucket
        s3_client.put_object(
            Bucket=bucket_name,
            Key=transcript_key,
            Body=transcript_text,
            ContentType='text/plain'
        )

        print(f"Successfully transcribed {object_key} and saved to {transcript_key}")

        return {
            'statusCode': 200,
            'body': json.dumps(f"Successfully transcribed {object_key}")
        }

    except ClientError as e:
        print(f"Error downloading or uploading files: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing the audio file: {str(e)}")
        }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Unexpected error: {str(e)}")
        }


lambda_handler({'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'ca-central-1',
                             'eventTime': '2025-02-19T18:55:39.248Z', 'eventName': 'ObjectCreated:Put',
                             'userIdentity': {'principalId': 'AWS:AIDAYPR4OKIJ4ZEMMTLLC'},
                             'requestParameters': {'sourceIPAddress': '173.35.0.74'},
                             'responseElements': {'x-amz-request-id': '4H3QEE4CESEAVJAH',
                                                  'x-amz-id-2': 'px4ecyksCZuu7QA6yB114guBP+KljSU+YNneds0arUtLSNCeHJxx7X1aRngrSpA7yD0YSAh3gm6B/XNdrEueVLAPoOLvDohi'},
                             's3': {'s3SchemaVersion': '1.0', 'configurationId': 'new-audio',
                                    'bucket': {'name': 'processed-transcripts-583168578067-ca-central-1',
                                               'ownerIdentity': {'principalId': 'A2M4GH1TABYC0R'},
                                               'arn': 'arn:aws:s3:::processed-transcripts-583168578067-ca-central-1'},
                                    'object': {'key': 'audio/26.mp3', 'size': 126333,
                                               'eTag': '8dc20233dcf1cc9649072e14db8920c6',
                                               'sequencer': '0067B6292B219FAAD5'}}}]}
               , 1)
