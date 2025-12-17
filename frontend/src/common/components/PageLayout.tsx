// src/common/components/PageLayout.tsx

import React from 'react';
import { Typography, Breadcrumb, Space, Button, Divider } from 'antd';
import { HomeOutlined } from '@ant-design/icons';
import type { ReactNode } from 'react';

const { Title, Text } = Typography;

interface PageLayoutProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: Array<{
    title: string;
    href?: string;
  }>;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
  showDivider?: boolean;
}

/**
 * Standardized page layout component for consistent structure across all pages
 * 
 * Features:
 * - Consistent spacing and typography
 * - Optional breadcrumbs navigation
 * - Action buttons area
 * - Responsive design
 * - Theme-aware styling
 */
const PageLayout: React.FC<PageLayoutProps> = ({
  title,
  subtitle,
  breadcrumbs,
  actions,
  children,
  className = '',
  showDivider = true,
}) => {
  return (
    <div 
      className={`page-layout ${className}`}
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}
    >
      {/* Page Header */}
      <div 
        className="page-header"
        style={{
          flexShrink: 0,
          padding: '16px 24px',
          backgroundColor: '#fff',
          borderBottom: showDivider ? '1px solid #f0f0f0' : 'none'
        }}
      >
        {/* Breadcrumbs */}
        {breadcrumbs && breadcrumbs.length > 0 && (
          <Breadcrumb style={{ marginBottom: 16 }}>
            <Breadcrumb.Item href="/dashboard">
              <HomeOutlined />
            </Breadcrumb.Item>
            {breadcrumbs.map((crumb, index) => (
              <Breadcrumb.Item key={index} href={crumb.href}>
                {crumb.title}
              </Breadcrumb.Item>
            ))}
          </Breadcrumb>
        )}

        {/* Title and Actions Row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <Title level={2} style={{ margin: 0, marginBottom: 4 }}>
              {title}
            </Title>
            {subtitle && (
              <Text type="secondary">
                {subtitle}
              </Text>
            )}
          </div>
          
          {actions && (
            <div style={{ flexShrink: 0 }}>
              <Space size="middle" wrap>
                {actions}
              </Space>
            </div>
          )}
        </div>
      </div>

      {/* Page Content */}
      <div 
        className="page-content"
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '24px',
          backgroundColor: '#f5f5f5'
        }}
      >
        <div style={{ height: '100%' }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default PageLayout;
