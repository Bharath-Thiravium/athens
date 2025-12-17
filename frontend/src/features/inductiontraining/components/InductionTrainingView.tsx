import React, { useCallback } from 'react';
import { Modal, Descriptions, Typography, Tag, Space } from 'antd';
import { BookOutlined, CalendarOutlined, EnvironmentOutlined, UserOutlined, ClockCircleOutlined, InfoCircleOutlined, EditOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import moment from 'moment';
import type { InductionTrainingData } from '../types';

const { Title, Text } = Typography;

// --- Interface Definition ---
interface InductionTrainingViewProps {
  inductionTraining: InductionTrainingData;
  visible: boolean;
  onClose: () => void;
}

// --- Styled Components for Themed UI ---
const StyledDescriptions = styled(Descriptions)`
  .ant-descriptions-item-label {
    font-weight: 500;
    color: var(--color-text-muted);
  }
  .ant-descriptions-item-content {
    color: var(--color-text-base);
  }
`;

// --- Component Definition ---
const InductionTrainingView: React.FC<InductionTrainingViewProps> = ({ inductionTraining, visible, onClose }) => {
  
  // Memoized helper function for status tags
  const getStatusTag = useCallback((status: string) => {
    switch (status?.toLowerCase()) {
      case 'planned':
        return <Tag color="blue">Planned</Tag>;
      case 'completed':
        return <Tag color="success">Completed</Tag>;
      case 'cancelled':
        return <Tag color="error">Cancelled</Tag>;
      default:
        return <Tag>{status || 'Unknown'}</Tag>;
    }
  }, []);

  // Helper to format dates consistently
  const formatDate = (dateStr: string | undefined) => {
    return dateStr ? moment(dateStr).format('MMMM D, YYYY, h:mm A') : 'N/A';
  };

  return (
    <Modal
      open={visible}
      title={<Title level={4} style={{color: 'var(--color-text-base)'}}>Induction Training Details</Title>}
      onCancel={onClose}
      footer={null} // This is a view-only modal
      width={700}
    >
      <StyledDescriptions bordered column={1} size="middle">
        <Descriptions.Item label={<Space><BookOutlined /> Title</Space>}>
          {inductionTraining.title}
        </Descriptions.Item>

        <Descriptions.Item label={<Space><CalendarOutlined /> Date</Space>}>
          {inductionTraining.date ? moment(inductionTraining.date).format('MMMM D, YYYY') : 'N/A'}
        </Descriptions.Item>
        
        <Descriptions.Item label={<Space><EnvironmentOutlined /> Location</Space>}>
          {inductionTraining.location}
        </Descriptions.Item>
        
        <Descriptions.Item label={<Space><UserOutlined /> Conducted By</Space>}>
          {inductionTraining.conducted_by}
        </Descriptions.Item>
        
        <Descriptions.Item label={<Space><InfoCircleOutlined /> Status</Space>}>
          {getStatusTag(inductionTraining.status)}
        </Descriptions.Item>

        <Descriptions.Item label={<Space><ClockCircleOutlined /> Created At</Space>}>
          {formatDate(inductionTraining.created_at)}
        </Descriptions.Item>
        
        <Descriptions.Item label={<Space><EditOutlined /> Last Updated</Space>}>
          {formatDate(inductionTraining.updated_at)}
        </Descriptions.Item>
      </StyledDescriptions>
    </Modal>
  );
};

export default InductionTrainingView;