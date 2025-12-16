import React from 'react';
import { Breadcrumb } from 'antd';
import IncidentReports from '../components/IncidentReports';

const ReportsPage: React.FC = () => {
  const getBreadcrumbItems = () => {
    return [
      { title: 'Home' },
      { title: 'Incident Management' },
      { title: 'Reports' }
    ];
  };

  return (
    <div style={{ padding: '24px' }}>
      <Breadcrumb style={{ marginBottom: '16px' }}>
        {getBreadcrumbItems().map((item, index) => (
          <Breadcrumb.Item key={index}>{item.title}</Breadcrumb.Item>
        ))}
      </Breadcrumb>
      
      <IncidentReports />
    </div>
  );
};

export default ReportsPage;
