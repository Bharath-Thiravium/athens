import React, { useState, useEffect } from 'react';
import { Card, Tabs, List, Typography, Tag, Button, Space, Empty, Spin } from 'antd';
import { BellOutlined, CheckOutlined, ReloadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useNotificationsContext } from '@common/contexts/NotificationsContext';
import type { Notification } from '@common/utils/webSocketNotificationService';

const { Title, Text } = Typography;

const NotificationsPage: React.FC = () => {
  const navigate = useNavigate();
  const { notifications, unreadCount, markAsRead, markAllAsRead, requestNotifications } = useNotificationsContext();
  const [activeTab, setActiveTab] = useState<'all' | 'unread'>('all');
  const [loading, setLoading] = useState(false);

  const filteredNotifications = activeTab === 'unread' 
    ? notifications.filter(n => !n.read)
    : notifications;

  const handleNotificationClick = async (notification: Notification) => {
    if (!notification.read) {
      await markAsRead(notification.id);
    }
    
    if (notification.link) {
      let targetLink = notification.link;
      
      // Normalize PTW links to /dashboard/ptw/view/:id
      if (targetLink.includes('/ptw/permits/') || targetLink.includes('/api/v1/ptw/permits/')) {
        const permitIdMatch = targetLink.match(/\/permits\/(\d+)/);
        if (permitIdMatch) {
          targetLink = `/dashboard/ptw/view/${permitIdMatch[1]}`;
        }
      }
      
      navigate(targetLink);
    }
  };

  const handleMarkAllRead = async () => {
    setLoading(true);
    await markAllAsRead();
    setLoading(false);
  };

  const handleRefresh = async () => {
    setLoading(true);
    await requestNotifications();
    setLoading(false);
  };

  const getNotificationTypeColor = (type: string) => {
    const colorMap: Record<string, string> = {
      ptw_verification: 'blue',
      ptw_approval: 'orange',
      ptw_approved: 'green',
      ptw_rejected: 'red',
      ptw_expiring: 'gold',
      ptw_submitted: 'cyan',
      ptw_activated: 'green',
      ptw_closeout_required: 'purple',
      ptw_isolation_pending: 'magenta',
      meeting_invitation: 'blue',
      approval: 'orange',
      general: 'default',
    };
    return colorMap[type] || 'default';
  };

  const getNotificationTypeLabel = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="p-6">
      <Card>
        <div className="flex items-center justify-between mb-4">
          <Title level={3} className="!mb-0">
            <BellOutlined className="mr-2" />
            Notifications
          </Title>
          <Space>
            <Button 
              icon={<ReloadOutlined />} 
              onClick={handleRefresh}
              loading={loading}
            >
              Refresh
            </Button>
            {unreadCount > 0 && (
              <Button 
                icon={<CheckOutlined />} 
                onClick={handleMarkAllRead}
                loading={loading}
              >
                Mark All Read
              </Button>
            )}
          </Space>
        </div>

        <Tabs
          activeKey={activeTab}
          onChange={(key) => setActiveTab(key as 'all' | 'unread')}
          items={[
            {
              key: 'all',
              label: `All (${notifications.length})`,
            },
            {
              key: 'unread',
              label: `Unread (${unreadCount})`,
            },
          ]}
        />

        {loading && notifications.length === 0 ? (
          <div className="text-center py-8">
            <Spin size="large" />
          </div>
        ) : filteredNotifications.length === 0 ? (
          <Empty
            image={<BellOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
            description={
              activeTab === 'unread' 
                ? 'No unread notifications' 
                : 'No notifications'
            }
          />
        ) : (
          <List
            dataSource={filteredNotifications}
            renderItem={(notification) => (
              <List.Item
                className={`cursor-pointer transition-colors ${
                  !notification.read ? 'bg-blue-50' : 'hover:bg-gray-50'
                }`}
                onClick={() => handleNotificationClick(notification)}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Text strong={!notification.read}>{notification.title}</Text>
                      {!notification.read && (
                        <div className="w-2 h-2 bg-blue-500 rounded-full" />
                      )}
                    </Space>
                  }
                  description={
                    <Space direction="vertical" size="small" className="w-full">
                      <Text>{notification.message}</Text>
                      <Space>
                        <Tag color={getNotificationTypeColor(notification.type)}>
                          {getNotificationTypeLabel(notification.type)}
                        </Tag>
                        <Text type="secondary" className="text-xs">
                          {new Date(notification.created_at).toLocaleString()}
                        </Text>
                      </Space>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
};

export default NotificationsPage;
