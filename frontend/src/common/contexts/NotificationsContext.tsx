import React, { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { useWebSocketNotificationService, type Notification } from '../utils/webSocketNotificationService';

interface NotificationsContextValue {
  notifications: Notification[];
  unreadCount: number;
  isConnected: boolean;
  sendNotification: (userId: string | number, payload: any) => Promise<boolean>;
  sendApprovalNotification: (userId: string | number, payload: any) => Promise<boolean>;
  markAsRead: (notificationId: string | number) => Promise<boolean>;
  markAllAsRead: () => Promise<boolean>;
  deleteNotification: (notificationId: string | number) => Promise<boolean>;
  requestNotifications: () => Promise<boolean>;
}

const NotificationsContext = createContext<NotificationsContextValue | undefined>(undefined);

interface NotificationsProviderProps {
  children: ReactNode;
}

export const NotificationsProvider: React.FC<NotificationsProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  const webSocketService = useWebSocketNotificationService();

  // Request notifications when connected
  useEffect(() => {
    if (webSocketService.isConnected) {
      setConnectionError(null);
      try {
        webSocketService.requestNotifications();
      } catch (err) {
        setConnectionError('Failed to request notifications');
      }
    } else {
      // Set a connection error if WebSocket is not connected after some time
      const timeout = setTimeout(() => {
        if (!webSocketService.isConnected) {
          setConnectionError('WebSocket connection failed. Notifications may not work properly.');
        }
      }, 5000); // Wait 5 seconds before showing error

      return () => clearTimeout(timeout);
    }
  }, [webSocketService.isConnected]);

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (!webSocketService.lastMessage) return;

    const message = webSocketService.lastMessage;

    switch (message.type) {
      case 'notification':
        // New notification received
        if (message.notification) {
          setNotifications(prev => {
            // Avoid duplicates
            const exists = prev.some(n => n.id === message.notification.id);
            if (exists) {
              return prev;
            }
            return [message.notification, ...prev];
          });
          
          if (!message.notification.read) {
            setUnreadCount(prev => prev + 1);
          }
        }
        break;

      case 'notifications_list':
        // Full list of notifications received
        if (message.notifications && Array.isArray(message.notifications)) {
          setNotifications(message.notifications);
          setUnreadCount(message.notifications.filter((n: Notification) => !n.read).length);
        }
        break;

      case 'notification_marked_read':
        // Notification marked as read
        if (message.notification_id) {
          setNotifications(prev =>
            prev.map(n =>
              n.id === message.notification_id
                ? { ...n, read: true, read_at: new Date().toISOString() }
                : n
            )
          );
          setUnreadCount(prev => Math.max(0, prev - 1));
        }
        break;

      case 'all_notifications_marked_read':
        // All notifications marked as read
        setNotifications(prev =>
          prev.map(n => ({ ...n, read: true, read_at: new Date().toISOString() }))
        );
        setUnreadCount(0);
        break;

      case 'notification_deleted':
        // Notification deleted
        if (message.notification_id) {
          setNotifications(prev => {
            const notification = prev.find(n => n.id === message.notification_id);
            const filtered = prev.filter(n => n.id !== message.notification_id);
            
            // Update unread count if deleted notification was unread
            if (notification && !notification.read) {
              setUnreadCount(prevCount => Math.max(0, prevCount - 1));
            }
            
            return filtered;
          });
        }
        break;

      case 'notification_sent':
        // Confirmation that notification was sent
        break;

      case 'error':
        // Error message
        break;

      default:
    }
  }, [webSocketService.lastMessage]);

  const contextValue: NotificationsContextValue = {
    notifications,
    unreadCount,
    isConnected: webSocketService.isConnected,
    
    sendNotification: async (userId, payload) => {
      try {
        // Check if the user ID is valid
        if (!userId) {
          return false;
        }
        
        // Log the WebSocket connection status
        
        const result = await webSocketService.sendNotification(userId, payload);
        if (result) {
        } else {
        }
        return result;
      } catch (error) {
        return false;
      }
    },
    
    sendApprovalNotification: async (userId, payload) => {
      try {
        const result = await webSocketService.sendApprovalNotification(userId, payload);
        if (result) {
        } else {
        }
        return result;
      } catch (error) {
        return false;
      }
    },
    
    markAsRead: async (notificationId) => {
      try {
        if (!webSocketService.isConnected) {
          return false;
        }
        return await Promise.resolve(webSocketService.markAsRead(notificationId));
      } catch (error) {
        return false;
      }
    },

    markAllAsRead: async () => {
      try {
        if (!webSocketService.isConnected) {
          return false;
        }
        return await Promise.resolve(webSocketService.markAllAsRead());
      } catch (error) {
        return false;
      }
    },

    deleteNotification: async (notificationId) => {
      try {
        if (!webSocketService.isConnected) {
          return false;
        }
        return await Promise.resolve(webSocketService.deleteNotification(notificationId));
      } catch (error) {
        return false;
      }
    },
    
    requestNotifications: async () => {
      try {
        return await Promise.resolve(webSocketService.requestNotifications());
      } catch (error) {
        return false;
      }
    },
  };

  return (
    <NotificationsContext.Provider value={contextValue}>
      {children}
    </NotificationsContext.Provider>
  );
};

export const useNotificationsContext = (): NotificationsContextValue => {
  const context = useContext(NotificationsContext);
  if (!context) {
    throw new Error('useNotificationsContext must be used within a NotificationsProvider');
  }
  return context;
};




