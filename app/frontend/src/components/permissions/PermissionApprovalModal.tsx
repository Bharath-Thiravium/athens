import React, { useState } from 'react';
import { Modal, Button, message, Descriptions, Input } from 'antd';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import api from '../../common/utils/axiosetup';

interface PermissionRequest {
  id: number;
  requester_name: string;
  permission_type: string;
  reason: string;
  object_name: string;
  created_at: string;
}

interface PermissionApprovalModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
  request: PermissionRequest | null;
}

const PermissionApprovalModal: React.FC<PermissionApprovalModalProps> = ({
  visible,
  onCancel,
  onSuccess,
  request
}) => {
  const [loading, setLoading] = useState(false);

  const handleApproval = async (action: 'approve' | 'deny') => {
    if (!request) return;
    
    setLoading(true);
    try {
      await api.post(`/api/v1/permissions/approve/${request.id}/`, {
        action: action
      });

      message.success(`Permission ${action}d successfully`);
      onSuccess();
    } catch (error: any) {
      message.error(error.response?.data?.error || `Failed to ${action} permission`);
    } finally {
      setLoading(false);
    }
  };

  if (!request) return null;

  return (
    <Modal
      title="Permission Request Approval"
      open={visible}
      onCancel={onCancel}
      footer={[
        <Button key="deny" danger onClick={() => handleApproval('deny')} loading={loading}>
          <CloseOutlined /> Deny
        </Button>,
        <Button key="approve" type="primary" onClick={() => handleApproval('approve')} loading={loading}>
          <CheckOutlined /> Approve
        </Button>
      ]}
      width={600}
    >
      <Descriptions column={1} bordered>
        <Descriptions.Item label="Requester">
          {request.requester_name}
        </Descriptions.Item>
        <Descriptions.Item label="Permission Type">
          {request.permission_type.charAt(0).toUpperCase() + request.permission_type.slice(1)}
        </Descriptions.Item>
        <Descriptions.Item label="Item">
          {request.object_name}
        </Descriptions.Item>
        <Descriptions.Item label="Request Date">
          {new Date(request.created_at).toLocaleString()}
        </Descriptions.Item>
        <Descriptions.Item label="Reason">
          <div className="whitespace-pre-wrap">{request.reason}</div>
        </Descriptions.Item>
      </Descriptions>
    </Modal>
  );
};

export default PermissionApprovalModal;