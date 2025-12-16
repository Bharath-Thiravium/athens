import React, { useState, useEffect } from 'react';
import { 
  Card, Descriptions, Tag, Button, Space, Tabs, Table, 
  Timeline, Modal, Form, Input, App, Spin, Row, Col, 
  Typography, Divider, DatePicker, Image, message, Select, Avatar
} from 'antd';
import { QrcodeOutlined } from '@ant-design/icons';
import { 
  CheckCircleOutlined, CloseCircleOutlined, 
  ExclamationCircleOutlined, ClockCircleOutlined,
  FileTextOutlined, HistoryOutlined,
  TeamOutlined, ToolOutlined, SafetyOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  getPermit, approvePermit, rejectPermit, startWork,
  completeWork, closePermit, requestExtension,
  submitForVerification, verifyPermit, rejectVerification,
  submitForApproval
} from '../api';
import * as Types from '../types';
import dayjs from 'dayjs';
import { useNotificationsContext } from '@common/contexts/NotificationsContext';
import useAuthStore from '@common/store/authStore';
import api from '@common/utils/axiosetup';
import PageLayout from '@common/components/PageLayout';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { TextArea } = Input;
const { confirm } = Modal;


const PermitDetail: React.FC = () => {
  const {message} = App.useApp();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [permit, setPermit] = useState<Types.Permit | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  
  // Modals
  const [approvalModal, setApprovalModal] = useState(false);
  const [rejectionModal, setRejectionModal] = useState(false);
  const [extensionModal, setExtensionModal] = useState(false);
  const [verificationModal, setVerificationModal] = useState(false);
  const [verificationRejectionModal, setVerificationRejectionModal] = useState(false);
  const [qrModal, setQrModal] = useState(false);
  const [qrImage, setQrImage] = useState<string | null>(null);
  const [qrLoading, setQrLoading] = useState(false);
  const [availableApprovers, setAvailableApprovers] = useState<any[]>([]);
  const [loadingApprovers, setLoadingApprovers] = useState(false);

  // Forms
  const [approvalForm] = Form.useForm();
  const [rejectionForm] = Form.useForm();
  const [extensionForm] = Form.useForm();
  const [verificationForm] = Form.useForm();
  const [verificationRejectionForm] = Form.useForm();
  
  const handleGenerateQR = async () => {
    if (!id) return;
    
    setQrLoading(true);
    try {
      const response = await api.get(`/api/v1/ptw/permits/${id}/generate_qr_code/`);
      setQrImage(response.data.qr_image);
      setQrModal(true);
      message.success('QR Code generated successfully');
    } catch (error) {
      message.error('Failed to generate QR code');
    } finally {
      setQrLoading(false);
    }
  };
  
  // Add notification context
  const { sendNotification } = useNotificationsContext();
  
  const fetchPermit = async () => {
    if (!id) return;

    setLoading(true);
    try {
      const response = await getPermit(parseInt(id));
      setPermit(response.data);
    } catch (error: any) {
      if (error?.response?.status === 401) {
        message.error('Authentication expired. Please login again.');
      } else if (error?.response?.status === 403) {
        message.error('You do not have permission to view this permit');
      } else {
        message.error('Failed to load permit details');
      }
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchPermit();
  }, [id]);
  
  const handleApprove = async () => {
    if (!id) return;
    
    try {
      await approvalForm.validateFields();
      const values = approvalForm.getFieldsValue();
      
      setActionLoading(true);
      await approvePermit(parseInt(id), values.comments);
      message.success('Permit approved successfully');
      
      // Send notification to permit creator
      if (permit?.created_by) {
        sendNotification(permit.created_by, {
          title: 'Permit Approved',
          message: `Your permit ${permit.permit_number} has been approved`,
          type: 'approval',
          data: {
            permitId: permit.id,
            permitNumber: permit.permit_number,
            action: 'approved'
          },
          link: `/ptw/permits/${permit.id}`
        });
      }
      
      setApprovalModal(false);
      fetchPermit();
    } catch (error) {
      message.error('Failed to approve permit');
    } finally {
      setActionLoading(false);
    }
  };
  
  const handleReject = async () => {
    if (!id) return;
    
    try {
      await rejectionForm.validateFields();
      const values = rejectionForm.getFieldsValue();
      
      setActionLoading(true);
      await rejectPermit(parseInt(id), values.comments);
      message.success('Permit rejected');
      
      // Send notification to permit creator
      if (permit?.created_by) {
        sendNotification(permit.created_by, {
          title: 'Permit Rejected',
          message: `Your permit ${permit.permit_number} has been rejected`,
          type: 'general',
          data: {
            permitId: permit.id,
            permitNumber: permit.permit_number,
            action: 'rejected',
            reason: values.comments
          },
          link: `/ptw/permits/${permit.id}`
        });
      }
      
      setRejectionModal(false);
      fetchPermit();
    } catch (error) {
      message.error('Failed to reject permit');
    } finally {
      setActionLoading(false);
    }
  };
  
  const handleStartWork = async () => {
    if (!id) return;
    
    confirm({
      title: 'Start Work',
      icon: <ExclamationCircleOutlined />,
      content: 'Are you sure you want to start work on this permit?',
      onOk: async () => {
        setActionLoading(true);
        try {
          await startWork(parseInt(id));
          message.success('Work started successfully');
          
          // Notify relevant stakeholders
          if (permit?.assigned_workers) {
            permit.assigned_workers.forEach(worker => {
              if (worker.worker_details?.id) {
                sendNotification(worker.worker_details.id, {
                  title: 'Work Started',
                  message: `Work has started for permit ${permit.permit_number}`,
                  type: 'general',
                  data: {
                    permitId: permit.id,
                    permitNumber: permit.permit_number,
                    action: 'started'
                  },
                  link: `/ptw/permits/${permit.id}`
                });
              }
            });
          }
          
          fetchPermit();
        } catch (error) {
          message.error('Failed to start work');
        } finally {
          setActionLoading(false);
        }
      }
    });
  };
  
  const handleCompleteWork = async () => {
    if (!id) return;
    
    confirm({
      title: 'Complete Work',
      icon: <ExclamationCircleOutlined />,
      content: 'Are you sure you want to mark this work as completed?',
      onOk: async () => {
        setActionLoading(true);
        try {
          await completeWork(parseInt(id));
          message.success('Work completed successfully');
          fetchPermit();
        } catch (error) {
          message.error('Failed to complete work');
        } finally {
          setActionLoading(false);
        }
      }
    });
  };
  
  const handleClosePermit = async () => {
    if (!id) return;
    
    confirm({
      title: 'Close Permit',
      icon: <ExclamationCircleOutlined />,
      content: 'Are you sure you want to close this permit?',
      onOk: async () => {
        setActionLoading(true);
        try {
          await closePermit(parseInt(id));
          message.success('Permit closed successfully');
          fetchPermit();
        } catch (error) {
          message.error('Failed to close permit');
        } finally {
          setActionLoading(false);
        }
      }
    });
  };
  
  const handleRequestExtension = async () => {
    if (!id) return;

    try {
      await extensionForm.validateFields();
      const values = extensionForm.getFieldsValue();

      setActionLoading(true);
      await requestExtension({
        permit: parseInt(id),
        new_end_time: values.new_end_time.toISOString(),
        reason: values.reason
      });
      message.success('Extension requested successfully');
      setExtensionModal(false);
      fetchPermit();
    } catch (error) {
      message.error('Failed to request extension');
    } finally {
      setActionLoading(false);
    }
  };

  const [selectedUserType, setSelectedUserType] = useState<string>('');
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  
  const fetchAvailableApprovers = async () => {
    setLoadingApprovers(true);
    try {
      // This method is no longer used - we use hierarchical selection instead
      return;
      if (response.ok) {
        const data = await response.json();
        setAvailableApprovers(data);
      }
    } catch (error) {
    } finally {
      setLoadingApprovers(false);
    }
  };
  
  const loadUsersByTypeAndGrade = async (userType: string, grade?: string) => {
    setLoadingApprovers(true);
    try {
      const params = new URLSearchParams({ user_type: userType });
      if (grade) {
        params.append('grade', grade);
      }
      const response = await api.get(`/authentication/api/team-members/get_users_by_type_and_grade/?${params}`);
      setAvailableApprovers(response.data.users || []);
    } catch (error) {
      message.error('Failed to load users');
    } finally {
      setLoadingApprovers(false);
    }
  };
  
  const handleUserTypeChange = (userType: string) => {
    setSelectedUserType(userType);
    setSelectedGrade('');
    setAvailableApprovers([]);
    verificationForm.setFieldsValue({ grade: undefined, selected_approver: undefined });
  };
  
  const handleGradeChange = (grade: string) => {
    setSelectedGrade(grade);
    verificationForm.setFieldsValue({ selected_approver: undefined });
    if (selectedUserType) {
      loadUsersByTypeAndGrade(selectedUserType, grade);
    }
  };

  const handleVerify = async () => {
    if (!id) return;

    try {
      await verificationForm.validateFields();
      const values = verificationForm.getFieldsValue();

      setActionLoading(true);
      
      // Call API with selected user type and grade
      const response = await api.post(`/api/v1/ptw/permits/${id}/verify/`, {
        action: 'approve',
        comments: values.comments || '',
        user_type: selectedUserType,
        grade: selectedGrade
      });

      message.success('Permit verified and sent for approval');
      
      // Send notification to all users of selected grade
      if (availableApprovers.length > 0) {
        availableApprovers.forEach(user => {
          sendNotification(user.id, {
            title: 'PTW Approval Required',
            message: `Permit ${permit?.permit_number} requires your approval`,
            type: 'ptw_approval',
            data: {
              permitId: permit?.id,
              permitNumber: permit?.permit_number,
              action: 'approval_required'
            },
            link: `/dashboard/ptw/view/${permit?.id}`
          });
        });
      }

      // Send notification to permit creator
      if (permit?.created_by) {
        sendNotification(permit.created_by, {
          title: 'Permit Verified',
          message: `Your permit ${permit.permit_number} has been verified and sent for approval`,
          type: 'ptw_verification',
          data: {
            permitId: permit.id,
            permitNumber: permit.permit_number,
            action: 'verified'
          },
          link: `/dashboard/ptw/view/${permit.id}`
        });
      }

      setVerificationModal(false);
      fetchPermit();
    } catch (error) {
      message.error('Failed to verify permit');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRejectVerification = async () => {
    if (!id) return;

    try {
      await verificationRejectionForm.validateFields();
      const values = verificationRejectionForm.getFieldsValue();

      setActionLoading(true);
      await rejectVerification(parseInt(id), values.comments);
      message.success('Permit verification rejected');

      // Send notification to permit creator
      if (permit?.created_by) {
        sendNotification(permit.created_by, {
          title: 'Permit Verification Rejected',
          message: `Your permit ${permit.permit_number} verification has been rejected`,
          type: 'verification',
          data: {
            permitId: permit.id,
            permitNumber: permit.permit_number,
            action: 'verification_rejected',
            reason: values.comments
          },
          link: `/dashboard/ptw/view/${permit.id}`
        });
      }

      setVerificationRejectionModal(false);
      fetchPermit();
    } catch (error) {
      message.error('Failed to reject verification');
    } finally {
      setActionLoading(false);
    }
  };
  
  const getStatusTag = (status: string) => {
    const statusConfig: Record<string, { color: string, icon: React.ReactNode }> = {
      draft: { color: 'default', icon: <FileTextOutlined /> },
      submitted: { color: 'processing', icon: <ClockCircleOutlined /> },
      under_review: { color: 'processing', icon: <ClockCircleOutlined /> },
      pending_approval: { color: 'orange', icon: <ClockCircleOutlined /> },
      approved: { color: 'green', icon: <CheckCircleOutlined /> },
      rejected: { color: 'red', icon: <CloseCircleOutlined /> },
      active: { color: 'blue', icon: <ToolOutlined /> },
      suspended: { color: 'purple', icon: <ExclamationCircleOutlined /> },
      completed: { color: 'cyan', icon: <CheckCircleOutlined /> },
      closed: { color: 'black', icon: <CheckCircleOutlined /> },
      cancelled: { color: 'magenta', icon: <CloseCircleOutlined /> },
      expired: { color: 'red', icon: <CloseCircleOutlined /> }
    };
    
    const config = statusConfig[status] || { color: 'default', icon: null };
    
    return (
      <Tag color={config.color} icon={config.icon}>
        {status.replace('_', ' ').toUpperCase()}
      </Tag>
    );
  };
  
  // Check if current user can verify this permit
  const canVerifyPermit = (permit: any) => {
    const authState = useAuthStore.getState();
    const { usertype, grade } = authState;

    console.log('canVerifyPermit debug:', {
      usertype,
      grade,
      permit_status: permit?.status,
      permit_creator: permit?.created_by_details?.admin_type,
      permit_creator_grade: permit?.created_by_details?.grade,
      full_auth_state: authState
    });

    if (!permit || !permit.created_by_details) {
      return false;
    }

    // EPC C grade can verify contractor permits
    if (usertype === 'epcuser' && grade === 'C' &&
        permit.created_by_details.admin_type === 'contractoruser') {
      return true;
    }

    // EPC B grade can verify EPC C grade permits
    if (usertype === 'epcuser' && grade === 'B' &&
        permit.created_by_details.admin_type === 'epcuser' &&
        permit.created_by_details.grade === 'C') {
      return true;
    }

    // Client B grade can verify Client C grade permits
    if (usertype === 'clientuser' && grade === 'B' &&
        permit.created_by_details.admin_type === 'clientuser' &&
        permit.created_by_details.grade === 'C') {
      return true;
    }

    return false;
  };

  // Check if current user can approve this permit
  const canApprovePermit = (permit: any) => {
    const authState = useAuthStore.getState();
    const { usertype, grade } = authState;

    console.log('canApprovePermit debug:', {
      usertype,
      grade,
      permit_status: permit?.status,
      permit_creator: permit?.created_by_details?.admin_type,
      permit_creator_grade: permit?.created_by_details?.grade,
      permit_verifier: permit?.verifier_details?.admin_type,
      full_auth_state: authState
    });

    if (!permit || !permit.created_by_details) {
      return false;
    }

    // Client C grade can approve contractor permits (verified by EPC)
    if (usertype === 'clientuser' && grade === 'C' &&
        permit.created_by_details.admin_type === 'contractoruser') {
      return true;
    }

    // Client B grade can approve Client C grade permits
    if (usertype === 'clientuser' && grade === 'B' &&
        permit.created_by_details.admin_type === 'clientuser' &&
        permit.created_by_details.grade === 'C') {
      return true;
    }

    // EPC B grade can approve EPC C grade permits
    if (usertype === 'epcuser' && grade === 'B' &&
        permit.created_by_details.admin_type === 'epcuser' &&
        permit.created_by_details.grade === 'C') {
      return true;
    }

    return false;
  };

  const renderActionButtons = () => {
    if (!permit) return null;

    const { status } = permit;

    console.log('renderActionButtons debug:', {
      permit_status: status,
      permit_id: permit.id,
      permit_number: permit.permit_number,
      canVerify: canVerifyPermit(permit),
      canApprove: canApprovePermit(permit),
      permit_object: permit
    });

    return (
      <Space>
        {status === 'draft' && (
          <Button type="primary" onClick={() => navigate(`/dashboard/ptw/edit/${id}`)}>
            Edit Permit
          </Button>
        )}

        {(status === 'submitted' || status === 'under_review') && canVerifyPermit(permit) && (
          <>
            <Button type="primary" onClick={() => {
              setVerificationModal(true);
            }}>
              Verify Permit
            </Button>
            <Button danger onClick={() => setVerificationRejectionModal(true)}>
              Reject Verification
            </Button>
          </>
        )}

        {(status === 'submitted' || status === 'under_review') && !canVerifyPermit(permit) && (
          <Button type="default" disabled>
            Awaiting Verification
          </Button>
        )}

        {status === 'pending_approval' && canApprovePermit(permit) && (
          <>
            <Button type="primary" onClick={() => setApprovalModal(true)}>
              Approve Permit
            </Button>
            <Button danger onClick={() => setRejectionModal(true)}>
              Reject Permit
            </Button>
          </>
        )}

        {status === 'pending_approval' && !canApprovePermit(permit) && (
          <Button type="default" disabled>
            {permit.approved_by_details ? 
              `Already approved by ${permit.approved_by_details.name}` : 
              'Awaiting Approval'
            }
          </Button>
        )}

        {status === 'approved' && (
          <Button type="primary" onClick={handleStartWork}>
            Start Work
          </Button>
        )}

        {status === 'active' && (
          <>
            <Button type="primary" onClick={handleCompleteWork}>
              Complete Work
            </Button>
            <Button onClick={() => setExtensionModal(true)}>
              Request Extension
            </Button>
          </>
        )}

        {status === 'completed' && (
          <Button type="primary" onClick={handleClosePermit}>
            Close Permit
          </Button>
        )}

        <Button onClick={() => navigate('/dashboard/ptw')}>
          Back to List
        </Button>
      </Space>
    );
  };
  
  if (loading) {
    return <Spin size="large" />;
  }
  
  if (!permit) {
    return <div>Permit not found</div>;
  }
  
  return (
    <PageLayout
      title={`Permit: ${permit.permit_number}`}
      subtitle={permit.permit_type_details?.name}
      breadcrumbs={[
        { title: 'PTW Management' },
        { title: 'Permits', href: '/dashboard/ptw' },
        { title: permit.permit_number }
      ]}
      actions={
        <>
          {getStatusTag(permit.status)}
          <Button 
            icon={<QrcodeOutlined />} 
            onClick={() => handleGenerateQR()}
            type="default"
            loading={qrLoading}
          >
            Generate QR
          </Button>
        </>
      }
    >
      <Card style={{ height: '100%' }}>
        
        <Descriptions bordered column={2}>
          <Descriptions.Item label="Permit Type">
            <Tag color={permit.permit_type_details?.color_code}>
              {permit.permit_type_details?.name}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Risk Level">
            {permit.permit_type_details?.risk_level.toUpperCase()}
          </Descriptions.Item>
          
          <Descriptions.Item label="Location">
            {permit.location}
          </Descriptions.Item>
          <Descriptions.Item label="Department">
            {permit.project?.department || 'N/A'}
          </Descriptions.Item>
          
          <Descriptions.Item label="Planned Start">
            {dayjs(permit.planned_start_time).format('YYYY-MM-DD HH:mm')}
          </Descriptions.Item>
          <Descriptions.Item label="Planned End">
            {dayjs(permit.planned_end_time).format('YYYY-MM-DD HH:mm')}
          </Descriptions.Item>
          
          <Descriptions.Item label="Actual Start" span={2}>
            {permit.actual_start_time 
              ? dayjs(permit.actual_start_time).format('YYYY-MM-DD HH:mm')
              : 'Not started yet'}
          </Descriptions.Item>
          
          <Descriptions.Item label="Actual End" span={2}>
            {permit.actual_end_time 
              ? dayjs(permit.actual_end_time).format('YYYY-MM-DD HH:mm')
              : 'Not completed yet'}
          </Descriptions.Item>
          
          <Descriptions.Item label="Created By" span={2}>
            {permit.created_by_details?.name || 'Unknown'}
          </Descriptions.Item>

          {permit.verifier && (
            <Descriptions.Item label="Verified By" span={2}>
              {permit.verifier_details?.name || 'Unknown'}
              {permit.verified_at && ` on ${dayjs(permit.verified_at).format('YYYY-MM-DD HH:mm')}`}
            </Descriptions.Item>
          )}

          {permit.verification_comments && (
            <Descriptions.Item label="Verification Comments" span={2}>
              {permit.verification_comments}
            </Descriptions.Item>
          )}

          {permit.approved_by && (
            <Descriptions.Item label="Approved By" span={2}>
              {permit.approved_by_details?.name || 'Unknown'}
              {permit.approved_at && ` on ${dayjs(permit.approved_at).format('YYYY-MM-DD HH:mm')}`}
            </Descriptions.Item>
          )}

          {permit.approval_comments && (
            <Descriptions.Item label="Approval Comments" span={2}>
              {permit.approval_comments}
            </Descriptions.Item>
          )}

          <Descriptions.Item label="Description" span={2}>
            {permit.description}
          </Descriptions.Item>
        </Descriptions>
        
        <Divider />
        
        <Tabs defaultActiveKey="1">
          <TabPane 
            tab={<span><SafetyOutlined />Risk Assessment</span>}
            key="1"
          >
            <Descriptions bordered column={1}>
  
              
              <Descriptions.Item label="Control Measures">
                {permit.control_measures}
              </Descriptions.Item>
              
              <Descriptions.Item label="PPE Requirements">
                {permit.ppe_requirements}
              </Descriptions.Item>
              
              <Descriptions.Item label="Emergency Procedures">
                {permit.emergency_procedures}
              </Descriptions.Item>
              
              <Descriptions.Item label="Risk Assessment Completed">
                {permit.risk_assessment_completed ? 'Yes' : 'No'}
              </Descriptions.Item>
            </Descriptions>
          </TabPane>
          
          <TabPane 
            tab={<span><TeamOutlined />Workers</span>}
            key="2"
          >
            <Table 
              dataSource={permit.assigned_workers || []}
              rowKey="id"
              pagination={false}
              columns={[
                {
                  title: 'Name',
                  dataIndex: ['worker_details', 'name'],
                  key: 'name',
                },
                {
                  title: 'Employee ID',
                  dataIndex: ['worker_details', 'employee_id'],
                  key: 'employee_id',
                },
                {
                  title: 'Position',
                  dataIndex: ['worker_details', 'position'],
                  key: 'position',
                },
                {
                  title: 'Assigned On',
                  dataIndex: 'assigned_at',
                  key: 'assigned_at',
                  render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
                }
              ]}
            />
          </TabPane>
          
          <TabPane 
            tab={<span><HistoryOutlined />Audit Trail</span>}
            key="3"
          >
            <Timeline mode="left">
              {permit.audit_trail?.map((audit: Types.PermitAudit) => (
                <Timeline.Item 
                  key={audit.id}
                  color={audit.action.includes('approved') ? 'green' : 
                         audit.action.includes('rejected') ? 'red' : 'blue'}
                >
                  <p>
                    <strong>{audit.action}</strong> by {audit.user_details?.name || 'System'}
                  </p>
                  <p>{dayjs(audit.timestamp).format('YYYY-MM-DD HH:mm:ss')}</p>
                  {audit.comments && <p>Comments: {audit.comments}</p>}
                </Timeline.Item>
              ))}
            </Timeline>
          </TabPane>
          
          {permit.requires_isolation && (
            <TabPane 
              tab={<span><ToolOutlined />Isolation</span>}
              key="4"
            >
              <Descriptions bordered column={1}>
                <Descriptions.Item label="Isolation Details">
                  {permit.isolation_details}
                </Descriptions.Item>
              </Descriptions>
            </TabPane>
          )}
        </Tabs>
        
        <Divider />
        
        <div className="permit-actions">
          {renderActionButtons()}
        </div>
      </Card>
      
      {/* Approval Modal */}
      <Modal
        title="Approve Permit"
        open={approvalModal}
        onOk={handleApprove}
        onCancel={() => setApprovalModal(false)}
        confirmLoading={actionLoading}
      >
        <Form form={approvalForm} layout="vertical">
          <Form.Item
            name="comments"
            label="Comments (Optional)"
          >
            <TextArea rows={4} placeholder="Add any comments or conditions" />
          </Form.Item>
        </Form>
      </Modal>
      
      {/* Rejection Modal */}
      <Modal
        title="Reject Permit"
        open={rejectionModal}
        onOk={handleReject}
        onCancel={() => setRejectionModal(false)}
        confirmLoading={actionLoading}
      >
        <Form form={rejectionForm} layout="vertical">
          <Form.Item
            name="comments"
            label="Reason for Rejection"
            rules={[{ required: true, message: 'Please provide a reason for rejection' }]}
          >
            <TextArea rows={4} placeholder="Explain why this permit is being rejected" />
          </Form.Item>
        </Form>
      </Modal>
      
      {/* Extension Request Modal */}
      <Modal
        title="Request Time Extension"
        open={extensionModal}
        onOk={handleRequestExtension}
        onCancel={() => setExtensionModal(false)}
        confirmLoading={actionLoading}
      >
        <Form form={extensionForm} layout="vertical">
          <Form.Item
            name="new_end_time"
            label="New End Time"
            rules={[{ required: true, message: 'Please select new end time' }]}
          >
            <DatePicker
              showTime
              format="YYYY-MM-DD HH:mm"
              style={{ width: '100%' }}
              disabledDate={(current) => {
                // Can't select days before today
                return current && current < dayjs().startOf('day');
              }}
            />
          </Form.Item>

          <Form.Item
            name="reason"
            label="Reason for Extension"
            rules={[{ required: true, message: 'Please provide a reason for extension' }]}
          >
            <TextArea rows={4} placeholder="Explain why an extension is needed" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Verification Modal */}
      <Modal
        title="Verify Permit"
        open={verificationModal}
        onOk={handleVerify}
        onCancel={() => {
          setVerificationModal(false);
          setSelectedUserType('');
          setSelectedGrade('');
          setAvailableApprovers([]);
          verificationForm.resetFields();
        }}
        confirmLoading={actionLoading}
        width={600}
        destroyOnClose
      >
        <Form form={verificationForm} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                name="user_type"
                label="User Type" 
                rules={[{ required: true, message: 'Please select user type' }]}
              >
                <Select 
                  placeholder="Select user type" 
                  onChange={handleUserTypeChange}
                  value={selectedUserType}
                >
                  <Select.Option value="clientuser">Client</Select.Option>
                  <Select.Option value="epcuser">EPC</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item 
                name="grade"
                label="Grade" 
                rules={[{ required: true, message: 'Please select grade' }]}
              >
                <Select 
                  placeholder="Select grade" 
                  onChange={handleGradeChange} 
                  disabled={!selectedUserType}
                  value={selectedGrade}
                >
                  {['A', 'B', 'C'].filter(grade => {
                    const authState = useAuthStore.getState();
                    const { usertype, grade: currentUserGrade } = authState;
                    
                    // Only hide C grade if current user is EPC with C grade
                    if (selectedUserType === 'epcuser' && usertype === 'epcuser' && currentUserGrade === 'C') {
                      return grade !== 'C';
                    }
                    
                    return true;
                  }).map(grade => (
                    <Select.Option key={grade} value={grade}>Grade {grade}</Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          

          
          <Form.Item
            name="comments"
            label="Verification Comments (Optional)"
          >
            <TextArea rows={4} placeholder="Add any verification comments or conditions" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Verification Rejection Modal */}
      <Modal
        title="Reject Verification"
        open={verificationRejectionModal}
        onOk={handleRejectVerification}
        onCancel={() => setVerificationRejectionModal(false)}
        confirmLoading={actionLoading}
      >
        <Form form={verificationRejectionForm} layout="vertical">
          <Form.Item
            name="comments"
            label="Reason for Rejection"
            rules={[{ required: true, message: 'Please provide a reason for rejection' }]}
          >
            <TextArea rows={4} placeholder="Explain why this permit verification is being rejected" />
          </Form.Item>
        </Form>
      </Modal>
      
      {/* QR Code Modal */}
      <Modal
        title="QR Code for Mobile Access"
        open={qrModal}
        onCancel={() => setQrModal(false)}
        footer={[
          <Button key="close" onClick={() => setQrModal(false)}>
            Close
          </Button>
        ]}
        width={400}
      >
        <div style={{ textAlign: 'center' }}>
          {qrImage && (
            <>
              <Image
                src={qrImage}
                alt="Permit QR Code"
                style={{ maxWidth: '300px', marginBottom: '16px' }}
              />
              <div>
                <Typography.Text type="secondary">
                  Scan this QR code with your mobile device to access permit details
                </Typography.Text>
              </div>
            </>
          )}
        </div>
      </Modal>
    </PageLayout>
  );
};

export default PermitDetail;