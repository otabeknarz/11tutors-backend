from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_upload_credentials(request):
    """
    Get VdoCipher upload credentials for video upload
    """
    try:
        title = request.data.get('title', 'Untitled Video')
        folder_id = request.data.get('folderId', 'root')
        
        # Request upload credentials from VdoCipher
        # VdoCipher expects title as query parameter, not in body
        # URL encode the title to handle special characters
        encoded_title = quote(title)
        vdocipher_url = f'https://dev.vdocipher.com/api/videos?title={encoded_title}&folderId={folder_id}'
        
        # Log the request details (without exposing the full API key)
        logger.info(f"Requesting VdoCipher credentials for: {title}")
        logger.debug(f"VdoCipher URL: {vdocipher_url}")
        logger.debug(f"API Key present: {bool(settings.VIDEO_SERVICE_SECRET_KEY)}")
        
        response = requests.put(
            vdocipher_url,
            headers=settings.VDOCIPHER_HEADERS
        )
        
        logger.info(f"VdoCipher response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Successfully got credentials, videoId: {data.get('videoId', 'N/A')}")
            logger.info(f"Upload URL: {data.get('uploadLink', 'N/A')}")
            logger.debug(f"Full response: {data}")
            return Response(data, status=status.HTTP_200_OK)
        else:
            logger.error(f"VdoCipher API error: {response.status_code}")
            logger.error(f"VdoCipher response: {response.text}")
            logger.error(f"Request URL: {vdocipher_url}")
            return Response(
                {
                    'error': 'Failed to get upload credentials from VdoCipher',
                    'details': response.text,
                    'status_code': response.status_code
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error getting VdoCipher credentials: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_otp(request, video_id):
    """
    Get OTP for video playback
    """
    try:
        payload = {'ttl': 300}  # 5 minutes
        
        response = requests.post(
            f'https://dev.vdocipher.com/api/videos/{video_id}/otp',
            json=payload,
            headers=settings.VDOCIPHER_HEADERS
        )
        
        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            logger.error(f"VdoCipher OTP error: {response.status_code} - {response.text}")
            return Response(
                {'error': 'Failed to get video OTP'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error getting video OTP: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
