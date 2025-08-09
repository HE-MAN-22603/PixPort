"""
External API-based background removal service
Uses remove.bg or similar services when local AI fails
"""

import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def remove_background_api(input_path: str, output_path: str) -> bool:
    """
    Remove background using external API service
    
    This is a backup when local AI models fail due to memory constraints
    """
    api_key = os.environ.get('REMOVEBG_API_KEY')
    
    if not api_key:
        logger.info("No external API key found, skipping API removal")
        return False
    
    try:
        logger.info("Using external API for background removal")
        
        # Read input image
        with open(input_path, 'rb') as input_file:
            image_data = input_file.read()
        
        # Call remove.bg API
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': image_data},
            data={'size': 'auto'},
            headers={'X-Api-Key': api_key},
            timeout=30
        )
        
        if response.status_code == 200:
            # Save result
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as output_file:
                output_file.write(response.content)
            
            logger.info(f"External API background removal successful: {output_path}")
            return True
        else:
            logger.error(f"API request failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"External API background removal failed: {e}")
        return False

def get_api_usage_info() -> Optional[dict]:
    """Get API usage information if key is available"""
    api_key = os.environ.get('REMOVEBG_API_KEY')
    
    if not api_key:
        return None
    
    try:
        response = requests.get(
            'https://api.remove.bg/v1.0/account',
            headers={'X-Api-Key': api_key},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception as e:
        logger.error(f"Failed to get API usage info: {e}")
        return None
