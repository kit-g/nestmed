import json
import os
import boto3
import openai
from datetime import datetime

s3 = boto3.client("s3")

BUCKET_NAME = os.getenv("PROCESSED_BUCKET")
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")

openai.api_key = OPENAI_API_KEY


def extract_documentation(transcript):
    documentation_elements = {
        "oasis_elements": [
            {"question": "What is the patient's cognitive status?", "answer": None},
            {"question": "What is the patient's mobility level?", "answer": None},
            {"question": "What is the patient's medical condition?", "answer": None},
        ],
        "vital_signs": {
            "heart_rate": None,
            "blood_pressure": None,
            "respiratory_rate": None,
            "blood_sugar": None,
        },
        "clinical_statement": {
            "summary": None,
        },
    }

    # Define OpenAI prompt structure for each element
    oasis_prompts = [
        "What is the patient's cognitive status?",
        "What is the patient's mobility level?",
        "What is the patient's medical condition?"
    ]

    vital_signs_prompt = "What is the patient's heart rate, blood pressure, respiratory rate, and blood sugar level in this transcript?"
    clinical_statement_prompt = "Provide a clinical statement summarizing the visit based on this transcript."

    # Process each element using OpenAI
    for i, prompt in enumerate(oasis_prompts):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": prompt + "\n" + transcript},
            ],
            max_tokens=150
        )
        documentation_elements["oasis_elements"][i]["answer"] = response['choices'][0]['message']['content'].strip()

    # Vital signs prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful medical assistant."},
            {"role": "user", "content": vital_signs_prompt + "\n" + transcript},
        ],
        max_tokens=150
    )
    documentation_elements["vital_signs"]["heart_rate"] = response['choices'][0]['message']['content'].strip()

    # Clinical statement prompt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful medical assistant."},
            {"role": "user", "content": clinical_statement_prompt + "\n" + transcript},
        ],
        max_tokens=150
    )
    documentation_elements["clinical_statement"]["summary"] = response['choices'][0]['message']['content'].strip()

    return documentation_elements


def lambda_handler(event, _):
    print(event)

    sns_message = event["Records"][0]["Sns"]["Message"]
    transcript_data = json.loads(sns_message)

    transcript_id = transcript_data["transcript_id"]
    transcript_text = transcript_data["text"]

    # Process transcript
    extracted_data = extract_documentation(transcript_text)

    # Store in S3
    timestamp = datetime.utcnow().isoformat()
    s3_key = f"processed_transcripts/{transcript_id}_{timestamp}.json"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps({"transcript_id": transcript_id, "extracted_data": extracted_data}),
        ContentType="application/json"
    )

    return {"status": "success", "s3_key": s3_key}
