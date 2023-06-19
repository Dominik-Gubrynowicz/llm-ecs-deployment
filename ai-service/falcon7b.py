from transformers import AutoTokenizer, BitsAndBytesConfig
import transformers
import torch
import boto3
import os
import json

req_queue_url = os.environ.get('REQUEST_QUEUE_URL')
res_queue_url = os.environ.get('RESPONSE_QUEUE_URL')
aws_region = os.environ.get('AWS_REGION', 'eu-west-1')

# session = boto3.Session(
#     aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
#     aws_session_token=os.environ.get('AWS_SESSION_TOKEN'),
#     region_name=aws_region
# )


sqs = boto3.client(
    'sqs',
    region_name=aws_region,
)
sqs.set_queue_attributes(
    QueueUrl=req_queue_url,
    Attributes={'ReceiveMessageWaitTimeSeconds': '20'}
)

model = "tiiuae/falcon-rw-1b"
quantization_config = BitsAndBytesConfig(
    llm_int8_enable_fp32_cpu_offload=True
)
tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    # load_in_8bit=True,
    device_map="auto",
    # quantization_config=quantization_config
)

def generate_response(message):
    print(message)

    sequences = pipeline(
        message,
        max_length=200,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
    )
    response: str = ''

    for seq in sequences:
        response += seq['generated_text']

    return response

print(f'Listening for requests from {req_queue_url}...')
while True:
    request = sqs.receive_message(
        QueueUrl=req_queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20
    )

    if 'Messages' not in request:
        continue
    
    print('Received request')
    for message in request['Messages']:
        receipt_handle = message['ReceiptHandle']
        try:
            # Parse the message body and get the hook_id.
            # This is the ID of the request that we want to generate a response for.
            payload = json.loads(message['Body'])
            hook_id = payload['hook_id']
            request_body = payload['request_body']

            print(f'Generating for hook ID: {hook_id}')
            res = generate_response( request_body )

            sqs.send_message(
                QueueUrl = res_queue_url,
                MessageBody = json.dumps({
                    'hook_id': hook_id,
                    'response_body': res
                })
            )

        except Exception as e:
            print('Error generating response', str(e))
            pass
        finally:
            sqs.delete_message(
                QueueUrl=req_queue_url,
                ReceiptHandle=receipt_handle
            )