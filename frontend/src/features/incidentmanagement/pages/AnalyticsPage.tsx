import React from 'react';
import { Breadcrumb } from 'antd';
import AnalyticsDashboard from '../components/AnalyticsDashboard';

const AnalyticsPage: React.FC = () => {
  const getBreadcrumbItems = () => {
    return [
      { title: 'Home' },
      { title: 'Incident Management' },
      { title: 'Analytics' }
    ];
  };

  return (
    <div style={{ padding: '24px' }}>
      <Breadcrumb style={{ marginBottom: '16px' }}>
        {getBreadcrumbItems().map((item, index) => (
          <Breadcrumb.Item key={index}>{item.title}</Breadcrumb.Item>
        ))}
      </Breadcrumb>
      
      <AnalyticsDashboard />
    </div>
  );
};

export default AnalyticsPage;
