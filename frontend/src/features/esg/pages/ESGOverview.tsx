import React from 'react';
import PageLayout from '../../../common/components/PageLayout';
import ESGOverviewDashboard from '../components/ESGOverviewDashboard';

const ESGOverview: React.FC = () => {
  return (
    <PageLayout
      title="ESG Performance Center"
      subtitle="Comprehensive Environmental, Social & Governance Analytics"
      breadcrumbs={[
        { title: 'ESG Management' },
        { title: 'Overview' }
      ]}
    >
      <ESGOverviewDashboard />
    </PageLayout>
  );
};

export default ESGOverview;