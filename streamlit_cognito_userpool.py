import boto3
from dotenv import load_dotenv
import os


load_dotenv()


# Initialize Cognito client
cognito_client = boto3.client('cognito-idp', 
                              region_name = os.getenv('AWS_DEFAULT_REGION'),  # Your AWS region
                              aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),  # Your AWS access key
                              aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'))  # Your AWS secret key

# Function to authenticate user
def authenticate_user(username, password):
    response = cognito_client.admin_initiate_auth(
        UserPoolId = os.getenv('UserPoolId'),  # Your User Pool ID
        ClientId = os.getenv('ClientId'),  # Your App Client ID
        AuthFlow='ALLOW_ADMIN_USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password,
        },
    )
    return response['AuthenticationResult']['IdToken']

# # Example usage in Streamlit
# import streamlit as st

# username = st.text_input('Username')
# password = st.text_input('Password', type='password')

# if st.button('Login'):
#     try:
#         id_token = authenticate_user(username, password)
#         st.success('Login successful')
#         st.write('ID Token:', id_token)
#     except Exception as e:
#         st.error(f'Login failed: {e}')
