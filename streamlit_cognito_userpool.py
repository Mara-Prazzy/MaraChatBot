import boto3

# Initialize Cognito client
cognito_client = boto3.client('cognito-idp', 
                              region_name='ca-central-1',  # Your AWS region
                              aws_access_key_id='ASIAXYKJR2KD6MVVYOVT',  # Your AWS access key
                              aws_secret_access_key='xdUf/ntLlTedbBNRf04y5y+t/GLqcIW9/VRxBFu9')  # Your AWS secret key

# Function to authenticate user
def authenticate_user(username, password):
    response = cognito_client.admin_initiate_auth(
        UserPoolId='ca-central-1_fnJ2CTAQT',  # Your User Pool ID
        ClientId='5va9h512kefleggchs4c9r3c99',  # Your App Client ID
        AuthFlow='ALLOW_ADMIN_USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password,
        },
    )
    return response['AuthenticationResult']['IdToken']

# Example usage in Streamlit
import streamlit as st

username = st.text_input('Username')
password = st.text_input('Password', type='password')

if st.button('Login'):
    try:
        id_token = authenticate_user(username, password)
        st.success('Login successful')
        st.write('ID Token:', id_token)
    except Exception as e:
        st.error(f'Login failed: {e}')