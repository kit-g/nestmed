# Transcript Processing with Django and AWS Lambda

This project manages audio transcription workflows using Django and AWS Lambda. It allows users to upload audio files, process them via OpenAI Whisper for transcription, and store the results in an S3 bucket. The following describes the setup and logic used in this project.

## Overview

The project consists of:

1. **Django Application**:
   - A web interface for uploading audio files and text transcripts.
   - A signal-based mechanism to trigger AWS Lambda functions for audio processing.

2. **AWS Lambda Functions**:
   - **AudioFileProcessingLambda**: Processes the uploaded audio file using OpenAI Whisper and saves the result to an S3 bucket.
   - **TranscriptProcessingFunction Lambda**: Triggered after a transcript is created to update metadata in S3 and other resources.

3. **AWS SAM Template**:
   - Defines the Lambda functions, S3 buckets, and IAM roles for permissions.


## Workflow

### 1. **Django Application**

The Django app serves as the front-end interface for users to upload audio files for transcription. The main components are:

- **Transcript Model**: Stores the audio file and the resulting transcription text.
- **Transcript Form**: A form allowing users to upload their audio files.
- **Transcript Created Signal**: When a new transcript is created, a signal triggers the associated Lambda function to process the audio file.

### 2. **Audio Upload to S3**

- After a user uploads an audio file, it’s saved in the `processed-transcripts-<account-id>-<region>` S3 bucket.
- The file is tagged with a unique identifier (`transcript.id`) to maintain consistency.

### 3. **AWS Lambda Functions**

- **AudioFileProcessingLambda**:
  - Triggered by S3 events when audio files are uploaded to the S3 bucket.
  - The function processes the audio file using OpenAI Whisper to generate a transcript.
  - The transcript text is saved back to S3 under the same file’s metadata.

- **TranscriptCreated Lambda**: This function manages metadata updates for the processed files stored in S3.

