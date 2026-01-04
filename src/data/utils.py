"""
Utility functions for data collection from various sources.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_api_key(service: str) -> str:
    """
    Get API key from environment variables.
    
    Args:
        service: Name of the service (e.g., 'YELP', 'GOOGLE_PLACES')
    
    Returns:
        API key as string
    """
    key_name = f"{service.upper()}_API_KEY"
    api_key = os.getenv(key_name)
    
    if not api_key:
        raise ValueError(f"{key_name} not found in .env file")
    
    return api_key
