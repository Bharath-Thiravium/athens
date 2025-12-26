import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Modal, message, Popconfirm, Tag, Card, Input, Image, Row, Col, Divider } from 'antd';
import { EditOutlined, EyeOutlined, DeleteOutlined, SearchOutlined, CalendarOutlined, CheckCircleOutlined, UploadOutlined } from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '@common/utils/axiosetup';
import PageLayout from '@common/components/PageLayout';
import useAuthStore from '@common/store/authStore';
import CommitmentModal from './CommitmentModal';
import ApprovalModal from './ApprovalModal';
import FixedPhotoUploadModal from './FixedPhotoUploadModal';
import dayjs from 'dayjs';

const { Search } = Input;

interface SafetyObservation {
  id: number;
  observationID: string;
  date: string;
  time: string;
  reportedBy: string;
  department: string;
  workLocation: string;
  typeOfObservation: string;
  classification: string[];
  severity: number;
  likelihood: number;
  riskScore: number;
  observationStatus: string;
  correctiveActionAssignedTo: string;
  commitmentDate: string;
  safetyObservationFound: string;
  correctivePreventiveAction: string;
  remarks: string;
  created_at: string;
  created_by: any;
  files: any[];
}

const SafetyObservationList: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [observations, setObservations] = useState<SafetyObservation[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [selectedObservation, setSelectedObservation] = useState<SafetyObservation | null>(null);

  // Workflow modals
  const [commitmentModalVisible, setCommitmentModalVisible] = useState(false);
  const [approvalModalVisible, setApprovalModalVisible] = useState(false);
  const [fixedPhotoModalVisible, setFixedPhotoModalVisible] = useState(false);
  const [workflowObservation, setWorkflowObservation] = useState<SafetyObservation | null>(null);

  const navigate = useNavigate();
  const { user, username } = useAuthStore();

  useEffect(() => {
    fetchObservations();
  }, []);

  // Handle view parameter from URL (for notifications)
  useEffect(() => {
    const viewObservationId = searchParams.get('view');
    if (viewObservationId && observations.length > 0) {
      const observationToView = observations.find(obs => obs.observationID === viewObservationId);
      if (observationToView) {
        handleView(observationToView);
        // Remove the view parameter from URL
        setSearchParams({});
      }
    }
  }, [observations, searchParams]);

  const fetchObservations = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/safetyobservation/');
      setObservations(response.data.results || response.data);
    } catch (error) {
      message.error('Failed to fetch safety observations');
    } finally {
      setLoading(false);
    }
  };

  const handleView = async (record: SafetyObservation) => {
    if (!record.observationID) {
      message.error('Invalid observation ID');
      return;
    }
    
    try {
      const response = await api.get(`/api/v1/safetyobservation/${record.observationID}/`);
      setSelectedObservation(response.data);
      setViewModalVisible(true);
    } catch (error: any) {
      console.error('View error:', error);
      console.error('Observation ID:', record.observationID);
      console.error('Full record:', record);
      message.error(`Failed to load observation details: ${error.response?.status || 'Unknown error'}`);
    }
  };

  const handleEdit = (record: SafetyObservation) => {
    if (!record.observationID) {
      message.error('Invalid observation ID');
      return;
    }
    navigate(`/dashboard/safetyobservation/edit/${record.observationID}`);
  };

  const handleDelete = async (record: SafetyObservation) => {
    if (!record.observationID) {
      message.error('Invalid observation ID');
      return;
    }
    
    try {
      await api.delete(`/api/v1/safetyobservation/${record.observationID}/`);
      message.success('Safety observation deleted successfully');
      fetchObservations();
    } catch (error: any) {
      console.error('Delete error:', error);
      console.error('Observation ID:', record.observationID);
      console.error('Full record:', record);
      message.error(`Failed to delete safety observation: ${error.response?.status || 'Unknown error'}`);
    }
  };

  // Workflow handlers
  const handleCommitment = (record: SafetyObservation) => {
    setWorkflowObservation(record);
    setCommitmentModalVisible(true);
  };

  const handleUploadFixedPhotos = (record: SafetyObservation) => {
    setWorkflowObservation(record);
    setFixedPhotoModalVisible(true);
  };

  const handleApproval = (record: SafetyObservation) => {
    setWorkflowObservation(record);
    setApprovalModalVisible(true);
  };

  const handleWorkflowSuccess = () => {
    setCommitmentModalVisible(false);
    setApprovalModalVisible(false);
    setFixedPhotoModalVisible(false);
    setWorkflowObservation(null);
    fetchObservations();
  };

  // Check if current user can perform actions
  const canProvideCommitment = (record: SafetyObservation) => {
    return record.correctiveActionAssignedTo === username &&
           record.observationStatus === 'open' &&
           !record.commitmentDate;
  };

  const canUploadFixedPhotos = (record: SafetyObservation) => {
    // ONLY the assigned person can upload fixed photos when status is in_progress
    return record.correctiveActionAssignedTo === username &&
           record.observationStatus === 'in_progress';
  };

  const canApprove = (record: SafetyObservation) => {
    return record.created_by?.username === username &&
           record.observationStatus === 'pending_verification';
  };

  const getSeverityColor = (severity: number) => {
    switch (severity) {
      case 1: return 'green';
      case 2: return 'orange';
      case 3: return 'red';
      case 4: return 'purple';
      default: return 'default';
    }
  };

  const getSeverityText = (severity: number) => {
    switch (severity) {
      case 1: return 'Low';
      case 2: return 'Medium';
      case 3: return 'High';
      case 4: return 'Critical';
      default: return 'Unknown';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'red';
      case 'in_progress': return 'orange';
      case 'pending_verification': return 'blue';
      case 'closed': return 'green';
      case 'rejected': return 'gray';
      default: return 'default';
    }
  };

  const columns = [
    {
      title: 'Observation ID',
      dataIndex: 'observationID',
      key: 'observationID',
      width: 150,
      filteredValue: searchText ? [searchText] : null,
      onFilter: (value: any, record: SafetyObservation) =>
        record.observationID.toLowerCase().includes(value.toLowerCase()) ||
        record.reportedBy.toLowerCase().includes(value.toLowerCase()) ||
        record.department.toLowerCase().includes(value.toLowerCase()),
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      width: 100,
      render: (date: string) => dayjs(date).format('DD/MM/YYYY'),
    },
    {
      title: 'Reported By',
      dataIndex: 'reportedBy',
      key: 'reportedBy',
      width: 120,
    },
    {
      title: 'Department',
      dataIndex: 'department',
      key: 'department',
      width: 100,
    },
    {
      title: 'Type',
      dataIndex: 'typeOfObservation',
      key: 'typeOfObservation',
      width: 120,
      render: (type: string) => type.replace('_', ' ').toUpperCase(),
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 80,
      render: (severity: number) => (
        <Tag color={getSeverityColor(severity)}>
          {getSeverityText(severity)}
        </Tag>
      ),
    },
    {
      title: 'Risk Score',
      dataIndex: 'riskScore',
      key: 'riskScore',
      width: 80,
      render: (score: number) => (
        <Tag color={score <= 3 ? 'green' : score <= 6 ? 'orange' : score <= 9 ? 'red' : 'purple'}>
          {score}
        </Tag>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'observationStatus',
      key: 'observationStatus',
      width: 120,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Commitment Date',
      dataIndex: 'commitmentDate',
      key: 'commitmentDate',
      width: 120,
      render: (date: string) => date ? dayjs(date).format('DD/MM/YYYY') : '-',
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_: any, record: SafetyObservation) => (
        <Space size="small" wrap>
          <Button
            type="primary"
            icon={<EyeOutlined />}
            size="small"
            onClick={() => handleView(record)}
          />

          {/* Commitment Button - for assigned person when status is open */}
          {canProvideCommitment(record) && (
            <Button
              type="default"
              icon={<CalendarOutlined />}
              size="small"
              onClick={() => handleCommitment(record)}
              style={{ backgroundColor: '#52c41a', borderColor: '#52c41a', color: 'white' }}
            >
              Commit
            </Button>
          )}

          {/* Upload Fixed Photos Button - ONLY for assigned person when status is in_progress */}
          {canUploadFixedPhotos(record) && (
            <Button
              type="default"
              icon={<UploadOutlined />}
              size="small"
              onClick={() => handleUploadFixedPhotos(record)}
              style={{ backgroundColor: '#1890ff', borderColor: '#1890ff', color: 'white' }}
            >
              Upload Fixed Photos
            </Button>
          )}

          {/* Approval Button - for creator when status is pending_verification */}
          {canApprove(record) && (
            <Button
              type="default"
              icon={<CheckCircleOutlined />}
              size="small"
              onClick={() => handleApproval(record)}
              style={{ backgroundColor: '#722ed1', borderColor: '#722ed1', color: 'white' }}
            >
              Review
            </Button>
          )}

          <Button
            type="default"
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEdit(record)}
          />

          <Popconfirm
            title="Are you sure you want to delete this observation?"
            onConfirm={() => handleDelete(record)}
            okText="Yes"
            cancelText="No"
          >
            <Button
              type="primary"
              danger
              icon={<DeleteOutlined />}
              size="small"
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <PageLayout
      title="Safety Observations List"
      subtitle="View and manage all safety observations"
    >
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Search
              placeholder="Search observations..."
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              onSearch={setSearchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 300 }}
            />
            <Button
              type="primary"
              onClick={() => navigate('/dashboard/safetyobservation/form')}
            >
              Create New Observation
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={observations}
          loading={loading}
          rowKey="id"
          scroll={{ x: 1200 }}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} observations`,
          }}
        />
      </Card>

      {/* View Modal */}
      <Modal
        title={`Safety Observation Details - ${selectedObservation?.observationID}`}
        open={viewModalVisible}
        onCancel={() => setViewModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            Close
          </Button>,
          // Show approval buttons if observation is pending verification and user is creator
          ...(selectedObservation?.observationStatus === 'pending_verification' &&
              selectedObservation?.created_by?.username === username ? [
            <Button
              key="reject"
              danger
              onClick={() => {
                setViewModalVisible(false);
                if (selectedObservation) {
                  setWorkflowObservation(selectedObservation);
                  setApprovalModalVisible(true);
                }
              }}
            >
              Review & Approve/Reject
            </Button>
          ] : [
            <Button
              key="edit"
              type="primary"
              onClick={() => {
                setViewModalVisible(false);
                if (selectedObservation) {
                  handleEdit(selectedObservation);
                }
              }}
            >
              Edit
            </Button>
          ])
        ]}
        width={900}
        style={{ top: 20 }}
      >
        {selectedObservation && (
          <div style={{ maxHeight: '70vh', overflowY: 'auto' }}>
            {/* Basic Information */}
            <Row gutter={16}>
              <Col span={12}>
                <p><strong>Date:</strong> {dayjs(selectedObservation.date).format('DD/MM/YYYY')}</p>
                <p><strong>Time:</strong> {selectedObservation.time}</p>
                <p><strong>Reported By:</strong> {selectedObservation.reportedBy}</p>
                <p><strong>Department:</strong> {selectedObservation.department}</p>
                <p><strong>Work Location:</strong> {selectedObservation.workLocation}</p>
              </Col>
              <Col span={12}>
                <p><strong>Type:</strong> {selectedObservation.typeOfObservation.replace('_', ' ')}</p>
                <p><strong>Classification:</strong> {selectedObservation.classification.join(', ')}</p>
                <p><strong>Severity:</strong> <Tag color={getSeverityColor(selectedObservation.severity)}>{getSeverityText(selectedObservation.severity)}</Tag></p>
                <p><strong>Risk Score:</strong> <Tag>{selectedObservation.riskScore}</Tag></p>
                <p><strong>Status:</strong> <Tag color={getStatusColor(selectedObservation.observationStatus)}>{selectedObservation.observationStatus.replace('_', ' ')}</Tag></p>
              </Col>
            </Row>

            <Divider />

            {/* Observation Details */}
            <p><strong>Observation Description:</strong></p>
            <p style={{ backgroundColor: '#f5f5f5', padding: 12, borderRadius: 6 }}>
              {selectedObservation.safetyObservationFound}
            </p>

            <p><strong>Corrective Action:</strong></p>
            <p style={{ backgroundColor: '#f5f5f5', padding: 12, borderRadius: 6 }}>
              {selectedObservation.correctivePreventiveAction}
            </p>

            <Row gutter={16}>
              <Col span={12}>
                <p><strong>Assigned To:</strong> {selectedObservation.correctiveActionAssignedTo}</p>
              </Col>
              <Col span={12}>
                <p><strong>Commitment Date:</strong> {selectedObservation.commitmentDate ? dayjs(selectedObservation.commitmentDate).format('DD/MM/YYYY') : 'Not set'}</p>
              </Col>
            </Row>

            <p><strong>Created:</strong> {dayjs(selectedObservation.created_at).format('DD/MM/YYYY HH:mm')}</p>

            {/* Photos Section */}
            {selectedObservation.files && selectedObservation.files.length > 0 && (
              <>
                <Divider orientation="left">Uploaded Photos</Divider>
                <Row gutter={16}>
                  {selectedObservation.files.map((file: any, index: number) => (
                    <Col key={index} span={8} style={{ marginBottom: 16 }}>
                      <div style={{ textAlign: 'center' }}>
                        <Image
                          width={200}
                          height={150}
                          src={file.file}
                          alt={`Photo ${index + 1}`}
                          style={{ objectFit: 'cover', borderRadius: 8 }}
                          preview={{
                            mask: <EyeOutlined />
                          }}
                        />
                        <p style={{ fontSize: 12, marginTop: 8, color: '#666' }}>
                          {file.file_name}
                        </p>
                        <p style={{ fontSize: 10, color: '#999' }}>
                          Uploaded: {dayjs(file.uploaded_at).format('DD/MM/YYYY HH:mm')}
                        </p>
                      </div>
                    </Col>
                  ))}
                </Row>
              </>
            )}

            {selectedObservation.remarks && (
              <>
                <Divider />
                <p><strong>Remarks:</strong></p>
                <p style={{ backgroundColor: '#f5f5f5', padding: 12, borderRadius: 6 }}>
                  {selectedObservation.remarks}
                </p>
              </>
            )}
          </div>
        )}
      </Modal>

      {/* Commitment Modal */}
      {workflowObservation && (
        <CommitmentModal
          visible={commitmentModalVisible}
          onCancel={() => setCommitmentModalVisible(false)}
          onSuccess={handleWorkflowSuccess}
          observationID={workflowObservation.observationID}
          observationDetails={{
            typeOfObservation: workflowObservation.typeOfObservation,
            severity: workflowObservation.severity,
            workLocation: workflowObservation.workLocation,
            safetyObservationFound: workflowObservation.safetyObservationFound,
          }}
        />
      )}

      {/* Approval Modal */}
      {workflowObservation && (
        <ApprovalModal
          visible={approvalModalVisible}
          onCancel={() => setApprovalModalVisible(false)}
          onSuccess={handleWorkflowSuccess}
          observationID={workflowObservation.observationID}
          observationData={workflowObservation}
        />
      )}

      {/* Fixed Photo Upload Modal */}
      {workflowObservation && (
        <FixedPhotoUploadModal
          visible={fixedPhotoModalVisible}
          onCancel={() => setFixedPhotoModalVisible(false)}
          onSuccess={handleWorkflowSuccess}
          observationID={workflowObservation.observationID}
          observationDetails={{
            typeOfObservation: workflowObservation.typeOfObservation,
            severity: workflowObservation.severity,
            workLocation: workflowObservation.workLocation,
            safetyObservationFound: workflowObservation.safetyObservationFound,
            correctivePreventiveAction: workflowObservation.correctivePreventiveAction,
          }}
        />
      )}
    </PageLayout>
  );
};

export default SafetyObservationList;
