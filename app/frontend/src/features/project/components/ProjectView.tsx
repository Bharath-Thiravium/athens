import React from 'react';
import { Modal, Tag, Typography, Button, Space, Row, Col } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
// FIX #1: Use dayjs for consistency with other components
import dayjs from 'dayjs';

const { Title, Text } = Typography;

interface Project {
  key: string;
  id: number;
  projectName: string;
  projectCategory: string;
  capacity: string;
  location: string;
  policeStation: string;
  policeContact: string;
  hospital: string;
  hospitalContact: string;
  commencementDate: string;
  deadlineDate?: string;
}

interface ProjectViewProps {
  project: Project | null;
  visible: boolean;
  onClose: () => void;
}

// A reusable component for displaying a single detail item
const DetailItem = ({ label, children }: { label: string; children: React.ReactNode }) => (
  <div>
    <Text type="secondary" className="block text-sm font-semibold !text-text-muted">{label}</Text>
    <div className="text-base text-text-base mt-1">{children}</div>
  </div>
);


const ProjectView: React.FC<ProjectViewProps> = ({ project, visible, onClose }) => {
  if (!project) {
    return null;
  }
  
  // The logic for displaying categories is preserved
  const getCategoryDisplay = (category: string) => {
    const categoryMap: { [key: string]: { color: string; label?: string } } = {
      'governments': { color: 'blue' },
      'manufacturing': { color: 'orange' },
      'construction': { color: 'volcano' },
      'chemical': { color: 'red' },
      'port_and_maritime': { color: 'cyan' },
      'power_and_energy': { color: 'gold' },
      'logistics': { color: 'lime' },
      'schools': { color: 'green' },
      'mining': { color: 'magenta' },
      'oil_and_gas': { color: 'purple' },
      'shopping_mall': { color: 'geekblue' },
      'aviation': { color: 'blue' },
      'residential': { color: 'green' },
      'commercial': { color: 'blue' },
      'industrial': { color: 'orange' },
      'infrastructure': { color: 'purple' },
    };
    const categoryInfo = categoryMap[category] || { color: 'default' };
    // FIX #2: Format the label for better readability
    const label = categoryInfo.label || (typeof category === 'string' && category ? category.charAt(0).toUpperCase() + category.slice(1).replace(/_/g, ' ') : 'Unknown');
    return <Tag color={categoryInfo.color}>{label}</Tag>;
  };
  
  // FIX #3: Format dates using dayjs
  const formattedCommencementDate = project.commencementDate
    ? dayjs(project.commencementDate).format('MMMM D, YYYY')
    : 'Not specified';

  const formattedDeadlineDate = project.deadlineDate
    ? dayjs(project.deadlineDate).format('MMMM D, YYYY')
    : 'Not specified';

  return (
    // The Modal, Tag, and Button components are all styled by your theme
    <Modal
      open={visible}
      onCancel={onClose}
      width={800}
      centered
      destroyOnHidden
      title={
        <Space align="center">
          <EyeOutlined className="text-xl" />
          <span className="font-semibold text-text-base text-lg">Project Details</span>
        </Space>
      }
      footer={
        <Button key="close" type="primary" onClick={onClose} size="large">
          Close
        </Button>
      }
    >
      <div className="pt-4 pb-2">
        <Row gutter={[32, 28]}>
            {/* Project Name */}
            <Col span={24}>
                <DetailItem label="Project Name">
                    <Title level={4} className="!mt-0 !mb-0 !text-text-base">{project.projectName}</Title>
                </DetailItem>
            </Col>

            {/* Category & Capacity */}
            <Col xs={24} sm={12}>
                <DetailItem label="Project Category">
                    {getCategoryDisplay(project.projectCategory)}
                </DetailItem>
            </Col>
            <Col xs={24} sm={12}>
                <DetailItem label="Capacity / Size">
                    {project.capacity}
                </DetailItem>
            </Col>
            
            {/* Location */}
            <Col span={24}>
                <DetailItem label="Location">
                    {project.location}
                </DetailItem>
            </Col>
            
            {/* Emergency Contacts */}
            <Col xs={24} sm={12}>
                <DetailItem label="Nearest Police Station">
                    {project.policeStation}
                </DetailItem>
            </Col>
            <Col xs={24} sm={12}>
                <DetailItem label="Police Station Contact">
                    {project.policeContact}
                </DetailItem>
            </Col>
            <Col xs={24} sm={12}>
                <DetailItem label="Nearest Hospital">
                    {project.hospital}
                </DetailItem>
            </Col>
            <Col xs={24} sm={12}>
                <DetailItem label="Hospital Contact">
                    {project.hospitalContact}
                </DetailItem>
            </Col>

            {/* Dates */}
            <Col xs={24} sm={12}>
                <DetailItem label="Commencement Date">
                    {formattedCommencementDate}
                </DetailItem>
            </Col>
            <Col xs={24} sm={12}>
                <DetailItem label="Deadline Date">
                    {formattedDeadlineDate}
                </DetailItem>
            </Col>
        </Row>
      </div>
    </Modal>
  );
};

export default ProjectView;
