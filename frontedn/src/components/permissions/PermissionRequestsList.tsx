import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, message, Card, Typography } from 'antd';
import { CheckOutlined, CloseOutlined, EyeOutlined } from '@ant-design/icons';
import api from '../../common/utils/axiosetup';

const { Title, Text } = Typography;

interface PermissionRequest {
  id: number;
  requester: string;
  permission_type: 'edit' | 'delete';
  reason: string;
  content_type: string;
  object_id: number;
  status: 'pending' | 'approved' | 'denied';
  created_at: string;
}

const PermissionRequestsList: React.FC = () => {
  const [requests, setRequests] = useState<PermissionRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<PermissionRequest | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/permissions/my-requests/');
      setRequests(response.data);
    } catch (error) {
      message.error('Failed to fetch permission requests');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleApprove = async (requestId: number) => {
    setActionLoading(true);
    try {
      await api.post(`/api/v1/permissions/approve/${requestId}/`, { action: 'approve' });
      message.success('Permission approved successfully');
      fetchRequests();
      setModalVisible(false);
    } catch (error) {
      message.error('Failed to approve permission');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeny = async (requestId: number) => {
    setActionLoading(true);
    try {
      await api.post(`/api/v1/permissions/approve/${requestId}/`, { action: 'deny' });
      message.success('Permission denied');
      fetchRequests();
      setModalVisible(false);
    } catch (error) {
      message.error('Failed to deny permission');
    } finally {
      setActionLoading(false);
    }
  };

  const columns = [
    {
      title: 'Requester',
      dataIndex: 'requester',
      key: 'requester',
    },
    {
      title: 'Permission Type',
      dataIndex: 'permission_type',
      key: 'permission_type',
      render: (type: string) => (
        <Tag color={type === 'edit' ? 'blue' : 'red'}>
          {type.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Object',
      key: 'object',
      render: (record: PermissionRequest) => (
        <Text>{record.content_type} #{record.object_id}</Text>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors = {
          pending: 'orange',
          approved: 'green',
          denied: 'red',
        };
        return <Tag color={colors[status as keyof typeof colors]}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Requested At',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (record: PermissionRequest) => (
        <Space>
          <Button
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedRequest(record);
              setModalVisible(true);
            }}
          >
            View
          </Button>
          {record.status === 'pending' && (
            <>
              <Button
                type="primary"
                icon={<CheckOutlined />}
                onClick={() => handleApprove(record.id)}
                loading={actionLoading}
              >
                Approve
              </Button>
              <Button
                danger
                icon={<CloseOutlined />}
                onClick={() => handleDeny(record.id)}
                loading={actionLoading}
              >
                Deny
              </Button>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={2}>Permission Requests</Title>
        <Table
          columns={columns}
          dataSource={requests}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="Permission Request Details"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={
          selectedRequest?.status === 'pending' ? [
            <Button key="deny" danger onClick={() => handleDeny(selectedRequest.id)} loading={actionLoading}>
              Deny
            </Button>,
            <Button key="approve" type="primary" onClick={() => handleApprove(selectedRequest.id)} loading={actionLoading}>
              Approve
            </Button>,
          ] : [
            <Button key="close" onClick={() => setModalVisible(false)}>
              Close
            </Button>
          ]
        }
      >
        {selectedRequest && (
          <div>
            <p><strong>Requester:</strong> {selectedRequest.requester}</p>
            <p><strong>Permission Type:</strong> {selectedRequest.permission_type}</p>
            <p><strong>Object:</strong> {selectedRequest.content_type} #{selectedRequest.object_id}</p>
            <p><strong>Reason:</strong></p>
            <p style={{ background: '#f5f5f5', padding: '12px', borderRadius: '4px' }}>
              {selectedRequest.reason}
            </p>
            <p><strong>Status:</strong> <Tag color={selectedRequest.status === 'pending' ? 'orange' : selectedRequest.status === 'approved' ? 'green' : 'red'}>{selectedRequest.status.toUpperCase()}</Tag></p>
            <p><strong>Requested At:</strong> {new Date(selectedRequest.created_at).toLocaleString()}</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default PermissionRequestsList;