import React, { useState, useEffect } from 'react';
import { Modal, Button, message, Card, Image, Space, Input, Row, Col, Divider, Tag } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import api from '@common/utils/axiosetup';

const { TextArea } = Input;

interface ReviewApprovalModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
  observationID: string;
}

interface SafetyObservation {
  observationID: string;
  date: string;
  time: string;
  reportedBy: string;
  department: string;
  workLocation: string;
  typeOfObservation: string;
  classification: string[];
  severity: number;
  riskScore: number;
  observationStatus: string;
  safetyObservationFound: string;
  correctivePreventiveAction: string;
  correctiveActionAssignedTo: string;
  commitmentDate: string;
  created_by: {
    username: string;
    name?: string;
  };
  files: Array<{
    id: number;
    file: string;
    file_name: string;
    file_type: string;
    uploaded_at: string;
  }>;
}

const ReviewApprovalModal: React.FC<ReviewApprovalModalProps> = ({
  visible,
  onCancel,
  onSuccess,
  observationID
}) => {
  const [loading, setLoading] = useState(false);
  const [observation, setObservation] = useState<SafetyObservation | null>(null);
  const [feedback, setFeedback] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (visible && observationID) {
      fetchObservationDetails();
    }
  }, [visible, observationID]);

  const fetchObservationDetails = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/v1/safetyobservation/${observationID}/`);
      setObservation(response.data);
    } catch (error) {
      message.error('Failed to load observation details');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    try {
      setActionLoading(true);
      
      await api.post(`/api/v1/safetyobservation/${observationID}/approve_observation/`, {
        approved: true,
        feedback: feedback
      });

      message.success('Observation approved and closed successfully!');
      onSuccess();
      
    } catch (error) {
      message.error('Failed to approve observation');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!feedback.trim()) {
      message.error('Please provide feedback for rejection');
      return;
    }

    try {
      setActionLoading(true);
      
      await api.post(`/api/v1/safetyobservation/${observationID}/approve_observation/`, {
        approved: false,
        feedback: feedback
      });

      message.success('Observation rejected and sent back for revision');
      onSuccess();
      
    } catch (error) {
      message.error('Failed to reject observation');
    } finally {
      setActionLoading(false);
    }
  };

  const getSeverityColor = (severity: number) => {
    switch (severity) {
      case 1: return 'green';
      case 2: return 'yellow';
      case 3: return 'orange';
      case 4: return 'red';
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

  const beforePhotos = observation?.files?.filter(file => file.file_type === 'before') || [];
  const fixedPhotos = observation?.files?.filter(file => file.file_type === 'fixed') || [];

  return (
    <Modal
      title={`Review & Approve - ${observation?.observationID}`}
      open={visible}
      onCancel={onCancel}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Cancel
        </Button>,
        <Button
          key="reject"
          danger
          icon={<CloseCircleOutlined />}
          loading={actionLoading}
          onClick={handleReject}
        >
          Reject
        </Button>,
        <Button
          key="approve"
          type="primary"
          icon={<CheckCircleOutlined />}
          loading={actionLoading}
          onClick={handleApprove}
        >
          Approve & Close
        </Button>,
      ]}
      width={1000}
      style={{ top: 20 }}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: '50px' }}>Loading...</div>
      ) : observation ? (
        <div>
          {/* Basic Information */}
          <Row gutter={16}>
            <Col span={12}>
              <p><strong>Date:</strong> {observation.date}</p>
              <p><strong>Time:</strong> {observation.time}</p>
              <p><strong>Reported By:</strong> {observation.reportedBy}</p>
              <p><strong>Department:</strong> {observation.department}</p>
              <p><strong>Work Location:</strong> {observation.workLocation}</p>
            </Col>
            <Col span={12}>
              <p><strong>Type:</strong> {observation.typeOfObservation.replace('_', ' ')}</p>
              <p><strong>Classification:</strong> {observation.classification.join(', ')}</p>
              <p><strong>Severity:</strong> <Tag color={getSeverityColor(observation.severity)}>{getSeverityText(observation.severity)}</Tag></p>
              <p><strong>Risk Score:</strong> <Tag>{observation.riskScore}</Tag></p>
              <p><strong>Assigned To:</strong> {observation.correctiveActionAssignedTo}</p>
            </Col>
          </Row>

          <Divider />

          {/* Observation Details */}
          <p><strong>Observation Description:</strong></p>
          <p style={{ backgroundColor: '#f5f5f5', padding: 12, borderRadius: 6 }}>
            {observation.safetyObservationFound}
          </p>

          <p><strong>Corrective Action:</strong></p>
          <p style={{ backgroundColor: '#f5f5f5', padding: 12, borderRadius: 6 }}>
            {observation.correctivePreventiveAction}
          </p>

          <Divider />

          {/* Photos Comparison */}
          <Row gutter={16}>
            <Col span={12}>
              <h4>Before Photos</h4>
              {beforePhotos.length > 0 ? (
                <Space wrap>
                  {beforePhotos.map((file) => (
                    <Image
                      key={file.id}
                      width={150}
                      height={150}
                      src={file.file}
                      alt={file.file_name}
                      style={{ objectFit: 'cover', borderRadius: 8 }}
                    />
                  ))}
                </Space>
              ) : (
                <p style={{ color: '#999' }}>No before photos uploaded</p>
              )}
            </Col>
            <Col span={12}>
              <h4>Fixed Photos</h4>
              {fixedPhotos.length > 0 ? (
                <Space wrap>
                  {fixedPhotos.map((file) => (
                    <Image
                      key={file.id}
                      width={150}
                      height={150}
                      src={file.file}
                      alt={file.file_name}
                      style={{ objectFit: 'cover', borderRadius: 8 }}
                    />
                  ))}
                </Space>
              ) : (
                <p style={{ color: '#999' }}>No fixed photos uploaded</p>
              )}
            </Col>
          </Row>

          <Divider />

          {/* Feedback Section */}
          <div>
            <p><strong>Feedback/Notes:</strong></p>
            <TextArea
              rows={4}
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Add your feedback here (required for rejection)..."
            />
          </div>
        </div>
      ) : null}
    </Modal>
  );
};

export default ReviewApprovalModal;
