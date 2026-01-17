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
  const [reconnectSignal, setReconnectSignal] = useState<number>(0);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  
  const setToken = useAuthStore((state) => state.setToken);
  
  useEffect(() => {
    let isActive = true;

    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }

    // Clean up any existing connection
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    
    // If no URL is provided, don't attempt to connect
    if (!url) {
      reconnectAttemptRef.current = 0;
      setReadyState(WebSocket.CLOSED);
      setIsConnected(false);
      return () => {
        isActive = false;
      };
    }
    
    // Validate token before creating WebSocket connection
    const connectWebSocket = async () => {
      try {
        // Add delay to ensure page is fully loaded
        await new Promise(resolve => setTimeout(resolve, 2000));

        if (!isActive) {
          return;
        }
        
        // Ensure we have a valid token before connecting
        const validToken = await authFix.getWebSocketToken();
        if (!validToken) {
          console.log('No valid token for WebSocket, using REST API fallback');
          setReadyState(WebSocket.CLOSED);
          setIsConnected(false);
          return;
        }

        // Update URL with the validated token
        const updatedUrl = url.replace(/token=[^&]*/, `token=${validToken}`);
        console.log('Attempting WebSocket connection to:', updatedUrl);

        // Add connection timeout
        const connectionTimeout = setTimeout(() => {
          if (socketRef.current && socketRef.current.readyState === WebSocket.CONNECTING) {
            console.log('WebSocket connection timeout');
            socketRef.current.close();
          }
        }, 10000); // 10 second timeout
        
        const socket = new WebSocket(updatedUrl);
        socketRef.current = socket;

        socket.addEventListener('open', () => {
          clearTimeout(connectionTimeout);
          console.log('WebSocket connected successfully');
          setReadyState(WebSocket.OPEN);
          setIsConnected(true);
          reconnectAttemptRef.current = 0;
        });

        socket.addEventListener('message', (event) => {
          try {
            const data = JSON.parse(event.data);

            // Handle authentication errors from WebSocket
            if (data.type === 'error') {
              console.log('WebSocket error:', data);
              if (data.code === 'token_invalid' || data.message?.includes('token')) {
                handleTokenRefresh();
                return;
              }
            }

            // Log successful connection establishment
            if (data.type === 'connection_established') {
              console.log('WebSocket connection established:', data);
            }

            setLastMessage(data);
          } catch (error) {
            console.error('WebSocket message parse error:', error);
          }
        });

        socket.addEventListener('close', (event) => {
          clearTimeout(connectionTimeout);
          console.log('WebSocket closed:', event.code, event.reason);
          setReadyState(WebSocket.CLOSED);
          setIsConnected(false);

          if (!isActive) {
            return;
          }
          
          // Handle different close codes
          if (event.code === 4001) {
            handleTokenRefresh();
          } else if (event.code === 1006 || event.code === 1005 || event.code === 1001) {
            const authState = useAuthStore.getState();
            if (authState.token && authState.isAuthenticated()) {
              const nextAttempt = Math.min(reconnectAttemptRef.current + 1, 5);
              reconnectAttemptRef.current = nextAttempt;
              const delay = Math.min(1000 * 2 ** nextAttempt, 30000);
              console.log('WebSocket connection lost, retrying in', delay, 'ms');
              if (!reconnectTimerRef.current) {
                reconnectTimerRef.current = setTimeout(() => {
                  reconnectTimerRef.current = null;
                  setReconnectSignal((value) => value + 1);
                }, delay);
              }
            } else {
              handleTokenRefresh();
            }
          }
        });
      
        socket.addEventListener('error', (event) => {
          clearTimeout(connectionTimeout);
          console.error('WebSocket error:', event);
          setReadyState(WebSocket.CLOSED);
          setIsConnected(false);

          // Check if this is a connection error that might be token-related
          const authState = useAuthStore.getState();
          if (!authState.isAuthenticated()) {
            handleTokenRefresh();
          }
        });
      
        return () => {
          if (socket && socket.readyState !== WebSocket.CLOSED) {
            socket.close();
          }
        };
      } catch (error) {
        console.error('WebSocket connection setup error:', error);
        setReadyState(WebSocket.CLOSED);
        setIsConnected(false);
        return () => {};
      }
    };
    
    connectWebSocket();
    return () => {
      isActive = false;
    };
  }, [url, reconnectSignal]);
  
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
        // Do not force logout on WS refresh failure; leave UI state untouched and allow manual retry
        console.log('WebSocket token refresh failed; keeping session intact.');
      }
    } catch (error) {
      // Avoid aggressive logout on WS errors; just log and allow manual recovery
      console.log('WebSocket token refresh error; ignoring to keep session intact.', error);
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



