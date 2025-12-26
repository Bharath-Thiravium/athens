from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from googletrans import Translator
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def translate_text(request):
    try:
        data = request.data
        text = data.get('text', '').strip()
        from_lang = data.get('from', 'en')
        to_lang = data.get('to', 'ta')
        
        if not text:
            return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        translator = Translator()
        result = translator.translate(text, src=from_lang, dest=to_lang)
        
        return Response({
            'translatedText': result.text,
            'originalText': text,
            'fromLanguage': from_lang,
            'toLanguage': to_lang
        })
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return Response({'error': 'Translation failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)