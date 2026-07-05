"""
sf_connection.py
----------------
Handles Salesforce authentication using credentials from .env
"""

import os
from dotenv import load_dotenv
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed

load_dotenv()


def get_connection() -> Salesforce:
    """
    Authenticate with Salesforce and return a connection object.
    Reads credentials from .env file.
    """
    username = os.getenv("SF_USERNAME")
    password = os.getenv("SF_PASSWORD")
    token    = os.getenv("SF_SECURITY_TOKEN")
    domain   = os.getenv("SF_DOMAIN", "login")  # 'test' for sandbox

    if not all([username, password, token]):
        raise ValueError(
            "Missing Salesforce credentials. "
            "Please fill in SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN in your .env file."
        )

    try:
        sf = Salesforce(
            username=username,
            password=password,
            security_token=token,
            domain=domain,
        )
        print(f"✅ Connected to Salesforce as {username}\n")
        return sf

    except SalesforceAuthenticationFailed as e:
        raise ConnectionError(f"❌ Salesforce login failed: {e}")
