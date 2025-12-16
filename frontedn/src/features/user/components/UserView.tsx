import React from 'react';
import { Descriptions, Modal, Typography, Avatar, Divider, Tag, Space } from 'antd';
import { UserOutlined, MailOutlined, PhoneOutlined, TeamOutlined, ApartmentOutlined, IdcardOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import type { UserData } from '../types';

const { Text, Title } = Typography;

// --- Prop Interface (Unchanged, already good) ---
interface UserViewProps {
  user: UserData | null;
  open: boolean;
  onClose: () => void;
}

// --- Styled Components for Themed UI ---

const ViewContainer = styled.div`
  // The Modal component provides the background color from the theme.
  // We just control the content's layout.
  padding: 8px 16px; 
`;

const ProfileHeader = styled.div`
  text-align: center;
  margin-bottom: 24px;
`;

const ThemedAvatar = styled(Avatar)`
  background-color: var(--color-primary);
  margin-bottom: 16px;
`;

const DetailSection = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled(Title)`
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px !important;
  font-size: 1rem !important; // Consistent size for section titles
  color: var(--color-text-base) !important;
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
`;

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

const UserView: React.FC<UserViewProps> = ({ user, open, onClose }) => {
  // If no user is provided, render nothing.
  if (!user) {
    return null;
  }

  return (
    <Modal 
      open={open}
      title={<Title level={4} style={{color: 'var(--color-text-base)'}}>User Details</Title>}
      footer={null} // This is a view-only modal
      onCancel={onClose}
      width={700}
      centered
      // No className or bodyStyle needed; the global theme and styled-components handle it.
    >
      <ViewContainer>
        <ProfileHeader>
          <ThemedAvatar size={80} icon={<UserOutlined />} />
          <Title level={3} style={{ margin: 0, color: 'var(--color-text-base)' }}>
            {user.name} {user.surname}
          </Title>
          <Text type="secondary" style={{ fontSize: 16 }}>
            {user.designation} • {user.department}
          </Text>
        </ProfileHeader>

        <Divider style={{ margin: '0 0 24px 0' }} />

        {/* Contact Information Section */}
        <DetailSection>
          <SectionTitle level={5}><MailOutlined />Contact Information</SectionTitle>
          <StyledDescriptions bordered column={1} size="small">
            <Descriptions.Item label="Email">
              <Text copyable={{ tooltips: ['Copy Email', 'Copied!'] }}>{user.email}</Text>
            </Descriptions.Item>
            <Descriptions.Item label="Phone Number">
              <Text copyable={{ tooltips: ['Copy Phone', 'Copied!'] }}>{user.phone_number}</Text>
            </Descriptions.Item>
          </StyledDescriptions>
        </DetailSection>

        {/* Professional Details Section */}
        <DetailSection>
          <SectionTitle level={5}><TeamOutlined />Professional Details</SectionTitle>
          <StyledDescriptions bordered column={1} size="small">
             <Descriptions.Item label="Username">
              <Tag color="purple">{user.username}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Company">
              {user.company_name || <Text type="secondary">Not Specified</Text>}
            </Descriptions.Item>
            <Descriptions.Item label="Department">
              <Tag color="blue">{user.department}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Designation">
              <Tag color="green">{user.designation}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Grade">
              {user.grade || <Text type="secondary">Not Specified</Text>}
            </Descriptions.Item>
          </StyledDescriptions>
        </DetailSection>

      </ViewContainer>
    </Modal>
  );
};

export default UserView;