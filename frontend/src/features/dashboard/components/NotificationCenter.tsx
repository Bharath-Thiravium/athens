// src/features/dashboard/components/NotificationCenter.tsx

import React from 'react';
import { Button, Card, Avatar, Space, Typography, Badge, Dropdown } from 'antd';
import { UserOutlined, BellOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '@common/store/authStore';
import type { Notification } from '@common/utils/webSocketNotificationService';

const { Text } = Typography;

interface NotificationCenterProps {
  notifications: Notification[];
  unreadCount: number;
  markAsRead: (id: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  onNotificationClick: (notification: Notification) => void;
  onMeetingResponse: (status: 'accepted' | 'rejected', invitation: {
    momId: any;
    userId: any;
    title: any;
    notificationId: any;
  }) => void;
}

const NotificationCenter: React.FC<NotificationCenterProps> = ({
  notifications,
  unreadCount,
  markAsRead,
  markAllAsRead,
  onNotificationClick,
  onMeetingResponse
}) => {
  const navigate = useNavigate();
  
  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
  };

  const notificationMenu = (
    <Card className="w-80" bodyStyle={{ padding: 0 }}>
      <div className="p-4 flex items-center justify-between border-b border-color-border">
        <Text strong className="text-color-text-base">Notifications</Text>
        {unreadCount > 0 && (
          <Button type="link" size="small" onClick={handleMarkAllAsRead}>
            Mark all as read
          </Button>
        )}
      </div>
      <div className="max-h-96 overflow-y-auto p-2 space-y-1">
        {notifications.length > 0 ? (
          notifications.map(notification => (
            <div 
              key={notification.id} 
              className={`p-3 rounded-lg transition-colors ${!notification.read ? 'bg-color-primary/10' : 'hover:bg-color-ui-hover'}`}
            >
              <Space align="start" className="w-full">
                <Avatar 
                  icon={<UserOutlined />} 
                  className={!notification.read ? '!bg-color-primary text-white' : ''} 
                />
                <div className="flex-1">
                  <Text strong className="block truncate text-color-text-base">
                    {notification.title}
                  </Text>
                  <Text className="text-xs line-clamp-2 text-color-text-muted">
                    {notification.message}
                  </Text>
                  {notification.type === 'meeting_invitation' && notification.data?.requiresResponse && (
                    <div className="mt-2 flex gap-2">
                      <Button 
                        size="small" 
                        type="primary" 
                        onClick={(e) => {
                          e.stopPropagation();
                          onMeetingResponse('accepted', {
                            momId: notification.data.momId,
                            userId: notification.data.userId,
                            title: notification.data.title,
                            notificationId: notification.id
                          });
                        }}
                      >
                        Accept
                      </Button>
                      <Button 
                        size="small" 
                        danger 
                        onClick={(e) => {
                          e.stopPropagation();
                          onMeetingResponse('rejected', {
                            momId: notification.data.momId,
                            userId: notification.data.userId,
                            title: notification.data.title,
                            notificationId: notification.id
                          });
                        }}
                      >
                        Reject
                      </Button>
                    </div>
                  )}
                  {notification.type !== 'meeting_invitation' && (
                    <div 
                      className="cursor-pointer" 
                      onClick={(e) => {
                        e.stopPropagation();
                        onNotificationClick(notification);
                      }}
                    >
                      <Text className="text-xs text-color-primary">Click to view details</Text>
                    </div>
                  )}
                </div>
                {!notification.read && (
                  <div className="mt-1 w-2 h-2 bg-color-primary rounded-full flex-shrink-0" />
                )}
              </Space>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-color-text-muted">
            <BellOutlined className="text-3xl mb-2 opacity-50" />
            <p>No new notifications</p>
          </div>
        )}
      </div>
    </Card>
  );

  return (
    <Dropdown 
      dropdownRender={() => notificationMenu} 
      placement="bottomRight" 
      arrow 
      trigger={['click']}
    >
      <Button 
        shape="circle" 
        icon={<Badge count={unreadCount} size="small"><BellOutlined /></Badge>} 
        size="large" 
        type="text" 
        className="!text-color-text-muted" 
      />
    </Dropdown>
  );
};

export default NotificationCenter;