import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_from_token(token):
    """
    Get user from JWT token with proper validation
    """
    try:
        # Use rest_framework_simplejwt for proper token validation
        UntypedToken(token)  # This validates the token
        
        # Decode the token to get user info
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        token_type = payload.get('token_type')
        
        # Ensure it's an access token
        if token_type != 'access':
            logger.warning(f"Invalid token type for WebSocket: {token_type}")
            return AnonymousUser()
            
        if user_id:
            user = User.objects.get(id=user_id, is_active=True)
            logger.info(f"WebSocket authentication successful for user {user.username}")
            return user
            
    except (InvalidToken, TokenError) as e:
        logger.warning(f"WebSocket token validation failed: {str(e)}")
    except jwt.ExpiredSignatureError:
        logger.warning("WebSocket token expired")
    except jwt.DecodeError:
        logger.warning("WebSocket token decode error")
    except jwt.InvalidTokenError:
        logger.warning("WebSocket invalid token")
    except User.DoesNotExist:
        logger.warning(f"WebSocket user not found for token: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket authentication error: {str(e)}")
        
    return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    JWT authentication middleware for WebSocket connections
    """
    
    async def __call__(self, scope, receive, send):
        # Get token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token')
        
        if token and len(token) > 0:
            token = token[0]
            logger.info(f"WebSocket connection attempt with token: {token[:20]}...")
            scope['user'] = await get_user_from_token(token)
        else:
            logger.warning("WebSocket connection attempt without token")
            scope['user'] = AnonymousUser()
        
        # Log the final authentication result
        user = scope['user']
        if user.is_anonymous:
            logger.warning("WebSocket connection: User is anonymous")
        else:
            logger.info(f"WebSocket connection: Authenticated as {user.username}")
        
        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """
    Middleware stack for JWT authentication
    """
    return JWTAuthMiddleware(inner)