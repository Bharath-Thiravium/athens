import React, { useMemo } from 'react';
import {
  Layout,
  Menu,
  Typography,
  Button,
  Avatar,
  Space,
  Dropdown,
  Badge,
  Card,
} from 'antd';
import {
  DashboardOutlined,
  ApartmentOutlined,
  TeamOutlined,
  CreditCardOutlined,
  AuditOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  BellOutlined,
  SunOutlined,
  MoonOutlined,
} from '@ant-design/icons';
import { useLocation, useNavigate, Navigate, Outlet } from 'react-router-dom';
import useAuthStore from '@common/store/authStore';
import { useTheme } from '@common/contexts/ThemeContext';
import { useResponsiveSidebar } from '@common/hooks/useResponsive';
import { useNotificationsContext } from '@common/contexts/NotificationsContext';
import PageLayout from '@common/components/PageLayout';
import '@common/styles/global.css';

const { Header, Content, Sider } = Layout;

const menuItems = [
  { key: '/superadmin/dashboard', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: '/superadmin/tenants', icon: <ApartmentOutlined />, label: 'Tenants (Companies)' },
  { key: '/superadmin/masters', icon: <TeamOutlined />, label: 'Masters' },
  { key: '/superadmin/subscriptions', icon: <CreditCardOutlined />, label: 'Subscriptions / Billing' },
  { key: '/superadmin/audit-logs', icon: <AuditOutlined />, label: 'Audit Logs' },
  { key: '/superadmin/settings', icon: <SettingOutlined />, label: 'Settings' },
];

const SuperadminLayout: React.FC = () => {
  const { token, isSuperAdmin, logout, username } = useAuthStore();
  const { setTheme, effectiveTheme } = useTheme();
  const { collapsed, mobileVisible, toggleSidebar, closeMobileSidebar, isMobile, isTablet } = useResponsiveSidebar();
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotificationsContext();
  const navigate = useNavigate();
  const location = useLocation();

  const selectedKey = useMemo(() => {
    const match = menuItems.find((item) => item.key !== 'logout' && location.pathname.startsWith(item.key));
    return match ? match.key : '/superadmin/dashboard';
  }, [location.pathname]);

  const handleMenuClick = (e: { key: string }) => {
    navigate(e.key);
    closeMobileSidebar();
  };

  const themeToggle = (
    <div className="flex items-center bg-color-ui-base p-1 rounded-full shadow-inner">
      <Button
        shape="circle"
        size="small"
        icon={<SunOutlined />}
        onClick={() => setTheme('light')}
        className={effectiveTheme === 'light' ? '!bg-color-primary !text-white' : '!bg-transparent !border-none !text-color-text-muted'}
      />
      <Button
        shape="circle"
        size="small"
        icon={<MoonOutlined />}
        onClick={() => setTheme('dark')}
        className={effectiveTheme === 'dark' ? '!bg-color-primary !text-white' : '!bg-transparent !border-none !text-color-text-muted'}
      />
    </div>
  );

  const profileMenu = {
    items: [
      { key: '/superadmin/settings', label: 'Settings', icon: <SettingOutlined /> },
      { type: 'divider' as const },
      { key: 'logout', label: 'Logout', icon: <LogoutOutlined />, danger: true },
    ],
    onClick: (info: any) => {
      if (info.key === 'logout') {
        logout();
        navigate('/login', { replace: true });
      } else {
        navigate(info.key);
      }
    },
  };

  const currentTitle = menuItems.find((i) => i.key === selectedKey)?.label || 'SaaS Control Plane';
  const sidebarWidth = (isMobile || isTablet) ? 280 : (collapsed ? 84 : 280);

  const notificationDropdown = (
    <Card className="w-80" bodyStyle={{ padding: 0 }}>
      <div className="p-4 flex items-center justify-between border-b border-color-border">
        <Typography.Text strong className="text-color-text-base">Notifications</Typography.Text>
        {unreadCount > 0 && (
          <Button type="link" size="small" onClick={markAllAsRead}>
            Mark all as read
          </Button>
        )}
      </div>
      <div className="max-h-96 overflow-y-auto p-3 space-y-2">
        {notifications.length > 0 ? (
          notifications.map((n) => (
            <div
              key={n.id}
              onClick={() => {
                if (!n.read) {
                  markAsRead(n.id);
                }
                if (n.link) navigate(n.link);
              }}
              className={`p-3 rounded-lg cursor-pointer transition-colors ${!n.read ? 'bg-color-primary/10' : 'hover:bg-color-ui-hover'}`}
            >
              <Space align="start">
                <Avatar size="small">{(n.title || 'N')[0]}</Avatar>
                <div>
                  <Typography.Text strong className="block truncate text-color-text-base">
                    {n.title || 'Notification'}
                  </Typography.Text>
                  <Typography.Text className="text-xs text-color-text-muted block">
                    {n.message || ''}
                  </Typography.Text>
                </div>
                {!n.read && <div className="mt-1 w-2 h-2 bg-color-primary rounded-full flex-shrink-0" />}
              </Space>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-color-text-muted">
            <BellOutlined className="text-2xl mb-2 opacity-50" />
            <p className="text-sm">No notifications</p>
          </div>
        )}
      </div>
    </Card>
  );

  // Guards (after hooks)
  if (!token) return <Navigate to="/login" replace />;
  if (!isSuperAdmin) return <Navigate to="/dashboard" replace />;

  return (
    <Layout className="dashboard-layout !bg-color-bg-base" hasSider>
      {(isMobile || isTablet) && mobileVisible && (
        <div
          onClick={closeMobileSidebar}
          style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.45)', zIndex: 999 }}
        />
      )}

      <Sider
        theme={effectiveTheme === 'dark' ? 'dark' : 'light'}
        width={sidebarWidth}
        collapsed={collapsed && !(isMobile || isTablet)}
        trigger={null}
        breakpoint="lg"
        className={`superadmin-sidebar ${effectiveTheme === 'dark' ? 'dark' : ''}`}
        style={{
          position: 'fixed',
          left: (isMobile || isTablet) ? (mobileVisible ? 0 : -sidebarWidth) : 0,
          top: 0,
          height: '100vh',
          overflow: 'hidden',
          zIndex: (isMobile || isTablet) ? 1001 : 50,
          transition: 'all 0.3s ease',
          boxShadow: effectiveTheme === 'dark' ? '1px 0 0 #1f2937' : '1px 0 0 #e5e7eb',
        }}
      >
        <div className="sidebar-header" style={{ padding: collapsed && !(isMobile || isTablet) ? '16px 8px' : '16px 24px' }}>
          <div className="sidebar-brand" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: 40,
                height: 40,
                backgroundColor: effectiveTheme === 'dark' ? '#111827' : '#f0f0f0',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                overflow: 'hidden',
              }}
            >
              <DashboardOutlined style={{ color: effectiveTheme === 'dark' ? '#e5e7eb' : '#555' }} />
            </div>
            {!collapsed && !isMobile && !isTablet && (
              <span style={{ fontWeight: 700, fontSize: 16, color: effectiveTheme === 'dark' ? '#e5e7eb' : '#0f172a' }}>
                Athens SaaS
              </span>
            )}
          </div>
          {(isMobile || isTablet) && (
            <Button
              type="text"
              icon={<MenuFoldOutlined />}
              onClick={closeMobileSidebar}
              style={{ padding: 8 }}
            />
          )}
        </div>
        <div style={{ height: 'calc(100% - 72px)', overflowY: 'auto', padding: collapsed && !(isMobile || isTablet) ? 8 : 12 }}>
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            onClick={handleMenuClick}
            theme={effectiveTheme === 'dark' ? 'dark' : 'light'}
            items={menuItems}
            style={{ borderRight: 0, background: 'transparent' }}
            inlineCollapsed={collapsed && !(isMobile || isTablet)}
          />
        </div>
      </Sider>

      <Layout
        className="!bg-transparent transition-all duration-300 h-screen flex flex-col"
        style={{
          marginLeft: (isMobile || isTablet) ? 0 : sidebarWidth,
        }}
      >
        <Header
          className="dashboard-header superadmin-header !px-6 flex justify-between items-center !h-20 !bg-color-bg-base !border-b !border-color-border"
          style={{
            left: (isMobile || isTablet) ? 0 : sidebarWidth,
          }}
        >
          <div className="flex items-center gap-3">
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={toggleSidebar}
              className="!h-10 !w-10 !text-xl !text-color-text-muted"
            />
            <Typography.Title level={4} style={{ margin: 0 }}>
              {currentTitle}
            </Typography.Title>
          </div>

          <div className="flex items-center gap-4">
            {themeToggle}

            <Dropdown overlay={notificationDropdown} placement="bottomRight" trigger={['click']}>
              <Button
                shape="circle"
                icon={
                  <Badge count={unreadCount} size="small">
                    <BellOutlined />
                  </Badge>
                }
                size="large"
                type="text"
                className="!text-color-text-muted"
              />
            </Dropdown>

            <Dropdown menu={profileMenu} placement="bottomRight" trigger={['click']}>
              <Avatar size="large" className="cursor-pointer">
                {(username || 'S')[0].toUpperCase()}
              </Avatar>
            </Dropdown>
          </div>
        </Header>

        <Content className="dashboard-content">
          <div
            className="dashboard-content-wrapper"
            style={{
              flex: 1,
              overflow: 'auto',
              padding: '20px 24px',
              minHeight: 0,
              maxWidth: '1200px',
              margin: '0 auto',
              width: '100%',
            }}
          >
            <PageLayout title={currentTitle} showDivider={false} className="saas-page-layout" style={{ width: '100%' }}>
              <Outlet />
            </PageLayout>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default SuperadminLayout;
