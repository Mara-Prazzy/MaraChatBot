import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import hmac
import hashlib
import base64

# Load environment variables from .env file
load_dotenv()

# Access environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_default_region = os.getenv('AWS_DEFAULT_REGION')
cognito_user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
cognito_app_client_id = os.getenv('COGNITO_APP_CLIENT_ID')
cognito_app_client_secret = os.getenv('COGNITO_APP_CLIENT_SECRET')  # Add client secret

# Initialize the Cognito client
cognito_client = boto3.client(
    'cognito-idp',
    region_name=aws_default_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Function to calculate the SECRET_HASH
def get_secret_hash(username, client_id, client_secret):
    message = username + client_id
    dig = hmac.new(str(client_secret).encode('utf-8'),
                   msg=str(message).encode('utf-8'),
                   digestmod=hashlib.sha256).digest()
    return base64.b64encode(dig).decode()

# Function to authenticate user
def authenticate_user(username, password):
    try:
        secret_hash = get_secret_hash(username, cognito_app_client_id, cognito_app_client_secret)
        response = cognito_client.admin_initiate_auth(
            UserPoolId=cognito_user_pool_id,
            ClientId=cognito_app_client_id,
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
                'SECRET_HASH': secret_hash
            },
        )
        return response['AuthenticationResult']['IdToken']
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

# # Example usage in Streamlit or Jupyter Notebook
# import streamlit as st

# username = st.text_input('Username')
# password = st.text_input('Password', type='password')

# if st.button('Login'):
#     id_token = authenticate_user(username, password)
#     if id_token:
#         st.success('Login successful')
#         st.write('ID Token:', id_token)
#     else:
#         st.error('Login failed')
