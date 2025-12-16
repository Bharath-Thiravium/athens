import React from 'react';
import WorkerList from '../components/WorkerList';
import { Typography } from 'antd';
import PageLayout from '@common/components/PageLayout';

const { Title } = Typography;

const WorkerPage: React.FC = () => {
  return (
    <PageLayout
      title="Worker Management"
      subtitle="Manage workers and their information"
      breadcrumbs={[
        { title: 'Workers' }
      ]}
    >
      <WorkerList />
    </PageLayout>
  );
};

export default WorkerPage;