import React, { useState } from 'react';
import { Modal, Form, Input, Button, message } from 'antd';
import api from '../../common/utils/axiosetup';

interface PermissionRequest {
  objectId: number;
  action: string;
  objectType: string;
  description: string;
}

interface PermissionRequestModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess?: () => void;
  request?: PermissionRequest | null;
  loading?: boolean;
  // Legacy props for backward compatibility
  permissionType?: 'edit' | 'delete';
  objectId?: number;
  contentType?: string;
  objectName?: string;
}

const PermissionRequestModal: React.FC<PermissionRequestModalProps> = ({
  visible,
  onCancel,
  onSuccess,
  request,
  loading: externalLoading = false,
  // Legacy props
  permissionType,
  objectId,
  contentType,
  objectName
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      // Use new request format if available, otherwise fall back to legacy
      const requestData = request ? {
        permission_type: request.action,
        reason: values.reason,
        object_type: request.objectType,
        object_id: request.objectId
      } : {
        permission_type: permissionType,
        reason: values.reason,
        app_label: contentType?.split('.')[0],
        model: contentType?.split('.')[1],
        object_id: objectId
      };
      
      await api.post('/api/v1/permissions/request/', requestData);

      message.success('Permission request sent successfully');
      form.resetFields();
      onSuccess?.();
    } catch (error: any) {
      message.error(error.response?.data?.error || 'Failed to send permission request');
    } finally {
      setLoading(false);
    }
  };

  // Get display values from request or legacy props
  const displayAction = request?.action || permissionType || 'unknown';
  const displayName = request?.description || objectName || 'Unknown item';
  
  return (
    <Modal
      title={`Request ${displayAction ? displayAction.charAt(0).toUpperCase() + displayAction.slice(1) : 'Unknown'} Permission`}
      open={visible}
      onCancel={onCancel}
      footer={null}
      width={500}
    >
      <div className="mb-4">
        <p><strong>Item:</strong> {displayName}</p>
        <p><strong>Action:</strong> {displayAction ? displayAction.charAt(0).toUpperCase() + displayAction.slice(1) : 'Unknown'}</p>
      </div>
      
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        <Form.Item
          name="reason"
          label="Reason for Request"
          rules={[{ required: true, message: 'Please provide a reason' }]}
        >
          <Input.TextArea
            rows={4}
            placeholder="Please explain why you need this permission..."
          />
        </Form.Item>

        <Form.Item className="mb-0">
          <div className="flex justify-end gap-2">
            <Button onClick={onCancel}>
              Cancel
            </Button>
            <Button type="primary" htmlType="submit" loading={loading || externalLoading}>
              Send Request
            </Button>
          </div>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default PermissionRequestModal;