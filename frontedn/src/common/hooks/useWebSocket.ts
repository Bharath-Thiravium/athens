// src/common/hooks/useWebSocket.ts

import { useEffect, useRef, useState, useCallback } from 'react';
import useAuthStore from '../store/authStore';
import api from '../utils/axiosetup';
import { authFix } from '../utils/authenticationFix';

export type NotificationType =
  | 'meeting'
  | 'meeting_response'
  | 'action_item'
  | 'general'
  | 'approval'
  | 'meeting_invitation'
  | 'meeting_scheduled'
  | 'mom_created'
  | 'task_assigned'
  | 'chat_message'
  | 'chat_message_delivered'
  | 'chat_message_read'
  | 'chat_file_shared'
  | 'safety_observation_assigned'
  | 'safety_observation_commitment'
  | 'safety_observation_completed'
  | 'safety_observation_approved'
  | 'safety_observation_closed'
  | 'ptw_verification'
  | 'ptw_approval'
  | 'ptw_approved'
  | 'ptw_rejected'
  | 'ptw_expiring'
  | 'permission_request'
  | 'permission_approved'
  | 'permission_denied';

export interface Notification {
  id: number | string;
  title: string;
  message: string;
  type: NotificationType;
  read: boolean;
  read_at?: string;
  created_at: string;
  data?: any;
  link?: string;
}

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface NotificationPayload {
  title: string;
  message: string;
  type: NotificationType;
  data?: any;
  link?: string;
  acceptLink?: string;
  rejectLink?: string;
}

export const useWebSocket = (url: string | null) => {
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [readyState, setReadyState] = useState<number>(WebSocket.CONNECTING);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const socketRef = useRef<WebSocket | null>(null);
  
  const setToken = useAuthStore((state) => state.setToken);
  
  useEffect(() => {
    // Clean up any existing connection
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    
    // If no URL is provided, don't attempt to connect
    if (!url) {
      setReadyState(WebSocket.CLOSED);
      setIsConnected(false);
      return;
    }
    
    // Validate token before creating WebSocket connection
    const connectWebSocket = async () => {
      try {
        // Ensure we have a valid token before connecting
        const validToken = await authFix.getWebSocketToken();
        if (!validToken) {
          setReadyState(WebSocket.CLOSED);
          setIsConnected(false);
          return;
        }

        // Update URL with the validated token
        const updatedUrl = url.replace(/token=[^&]*/, `token=${validToken}`);

        // Add connection timeout
        const connectionTimeout = setTimeout(() => {
          if (socketRef.current && socketRef.current.readyState === WebSocket.CONNECTING) {
            socketRef.current.close();
          }
        }, 10000); // 10 second timeout
        
        const socket = new WebSocket(updatedUrl);
        socketRef.current = socket;

        socket.addEventListener('open', () => {
          clearTimeout(connectionTimeout);
          setReadyState(WebSocket.OPEN);
          setIsConnected(true);
        });

        socket.addEventListener('message', (event) => {
          try {
            const data = JSON.parse(event.data);

            // Handle authentication errors from WebSocket
            if (data.type === 'error') {
              if (data.code === 'token_invalid' || data.message?.includes('token')) {
                handleTokenRefresh();
                return;
              }
            }

            // Log successful connection establishment
            if (data.type === 'connection_established') {
            }

            setLastMessage(data);
          } catch (error) {
          }
        });

        socket.addEventListener('close', (event) => {
          clearTimeout(connectionTimeout);
          setReadyState(WebSocket.CLOSED);
          setIsConnected(false);
          
          // Handle different close codes
          if (event.code === 4001) {
            handleTokenRefresh();
          } else if (event.code === 1006) {
            // For abnormal closures, check if we should attempt reconnection
            const authState = useAuthStore.getState();
            if (authState.token && authState.isAuthenticated()) {
              // Connection lost but user is still authenticated
            } else {
              handleTokenRefresh();
            }
          }
        });
      
      socket.addEventListener('error', (event) => {
        clearTimeout(connectionTimeout);
        setReadyState(WebSocket.CLOSED);
        setIsConnected(false);

        // Check if this is a connection error that might be token-related
        const authState = useAuthStore.getState();
        if (!authState.isAuthenticated()) {
          handleTokenRefresh();
        } else {
        }
      });
      
        return () => {
          if (socket && socket.readyState !== WebSocket.CLOSED) {
            socket.close();
          }
        };
      } catch (error) {
        setReadyState(WebSocket.CLOSED);
        setIsConnected(false);
        return () => {};
      }
    };
    
    connectWebSocket();
  }, [url]);
  
  // Handle token refresh when WebSocket authentication fails
  const handleTokenRefresh = async () => {
    try {
      
      const newToken = await authFix.ensureValidToken();
      if (newToken) {
        // The WebSocket will reconnect automatically when the URL changes due to new token
        // Force a small delay to ensure the auth store is updated
        setTimeout(() => {
        }, 100);
      } else {
        authFix.forceLogout('WebSocket token refresh failed');
      }
    } catch (error) {
      authFix.forceLogout('WebSocket token refresh error');
    }
  };
  
  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(message));
      return true;
    }
    return false;
  }, []);

  // Add a fallback REST API method for sending notifications
  const sendNotificationViaREST = async (userId: string | number, payload: NotificationPayload): Promise<boolean> => {
    try {
      const response = await api.post('/authentication/notifications/create/', {
        user_id: userId,
        title: payload.title,
        message: payload.message,
        type: payload.type,
        data: payload.data,
        link: payload.link
      });
      
      return response.data.success === true;
    } catch (error) {
      return false;
    }
  };

  // Update the sendNotification function to use the REST API fallback
  const sendNotification = async (userId: string | number, payload: NotificationPayload): Promise<boolean> => {
    // Try WebSocket first
    if (isConnected) {
      try {
        // Destructure the `type` from the payload and rename it to avoid collision.
        const { type: notificationType, ...restOfPayload } = payload;
        
        const message = {
          type: 'send_notification', // This is the WebSocket command
          user_id: userId,
          notification_type: notificationType, // This is the notification's own type (e.g., 'general')
          ...restOfPayload, // This contains title, message, data, etc.
        };
        
        const result = await sendMessage(message);
        if (result) return true;
      } catch (error) {
      }
    }
    
    // Fall back to REST API if WebSocket fails or is not connected
    return sendNotificationViaREST(userId, payload);
  };

  const markNotificationAsRead = useCallback((notificationId: string | number) => {
    return sendMessage({ type: 'mark_read', notification_id: notificationId });
  }, [sendMessage]);

  const markAllNotificationsAsRead = useCallback(() => {
    return sendMessage({ type: 'mark_all_read' });
  }, [sendMessage]);

  const deleteNotification = useCallback((notificationId: string | number) => {
    return sendMessage({ type: 'delete_notification', notification_id: notificationId });
  }, [sendMessage]);

  const requestNotifications = useCallback(() => {
    return sendMessage({ type: 'get_notifications' });
  }, [sendMessage]);
  
  const reconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
    }
  }, []);
  
  return { 
    lastMessage, 
    readyState, 
    isConnected,
    sendMessage, 
    sendNotification,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    deleteNotification,
    requestNotifications,
    reconnect 
  };
};





