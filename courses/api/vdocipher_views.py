from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
import logging

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
        vdocipher_url = 'https://dev.vdocipher.com/api/videos'
        
        payload = {
            'title': title,
            'folderId': folder_id
        }
        
        response = requests.put(
            vdocipher_url,
            json=payload,
            headers=settings.VDOCIPHER_HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            return Response(data, status=status.HTTP_200_OK)
        else:
            logger.error(f"VdoCipher API error: {response.status_code} - {response.text}")
            return Response(
                {'error': 'Failed to get upload credentials from VdoCipher'},
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
