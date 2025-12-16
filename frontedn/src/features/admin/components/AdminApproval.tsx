import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Space, Alert, Typography, message } from 'antd';
import { UserOutlined, BankOutlined, PhoneOutlined, CheckOutlined, EditOutlined } from '@ant-design/icons';
import { useOutletContext } from 'react-router-dom';
import api from '@common/utils/axiosetup';
import { useNotificationsContext } from '../../../common/contexts/NotificationsContext';
import type { NotificationType } from '../../../common/utils/webSocketNotificationService';
import PageLayout from '@common/components/PageLayout';

const { Title } = Typography;

interface AdminApprovalData {
  username: string;
  name?: string;
  company_name: string;
  registered_address: string;
  phone_number: string;
  pan_number?: string;
  gst_number?: string;
}

interface AdminApprovalProps {
  adminToApprove?: any | null;
  onAdminApprovalSuccess?: (id: number) => void;
}

const AdminApproval: React.FC = () => {
  const { adminToApprove, onAdminApprovalSuccess } = useOutletContext<{
    adminToApprove?: any | null;
    onAdminApprovalSuccess?: (id: number) => void;
  }>();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [approved, setApproved] = useState(false);
  const [editMode, setEditMode] = useState(true); // Start in edit mode by default
  const [localAdminToApprove, setLocalAdminToApprove] = useState<any | null>(null);
  const [fetchingPending, setFetchingPending] = useState(false);
  const [approvedUserId, setApprovedUserId] = useState<number | null>(null); // Track approved user
  const { sendNotification, notifications } = useNotificationsContext();

  // Use adminToApprove from context if available, otherwise use local state
  const currentAdminToApprove = adminToApprove || localAdminToApprove;

  // Reset approval state when adminToApprove changes (new admin to approve)
  useEffect(() => {
    if (adminToApprove && adminToApprove.user !== approvedUserId) {
      setApproved(false);
      setApprovedUserId(null);
    }
  }, [adminToApprove, approvedUserId]);

  // Fetch pending admin details if none provided through context
  useEffect(() => {
    const fetchPendingAdminDetails = async () => {
      // Don't fetch if we just approved someone or already have data
      if (!adminToApprove && !localAdminToApprove && !approved && !approvedUserId) {
        setFetchingPending(true);

        // Check if we recently approved someone in this session
        const recentlyApproved = sessionStorage.getItem('recently_approved_admin');

        try {

          // Try to get pending admin details from notifications
          const pendingNotification = notifications.find(n =>
            n.data?.formType === 'admindetail' &&
            !n.read &&
            n.data?.userId
          );


          if (pendingNotification?.data?.userId) {
            const userId = pendingNotification.data.userId;

            // Skip if this is the user we recently approved
            if (recentlyApproved && userId.toString() === recentlyApproved) {
            } else {
              try {
                const res = await api.get(`/authentication/admin/pending/${userId}/`);
                if (res.data) {
                  setLocalAdminToApprove(res.data);
                } else {
                }
              } catch (error: any) {
                if (error.response?.status === 404) {
                }
              }
            }
          } else {

            // Fallback: Try to find any pending admin details from recent notifications
            const recentAdminNotifications = notifications
              .filter(n => n.data?.formType === 'admindetail' && n.data?.userId)
              .sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime())
              .slice(0, 5); // Check last 5 admin notifications


            for (const notification of recentAdminNotifications) {
              try {
                const userId = notification.data?.userId;
                // Skip if this is the user we just approved or recently approved
                if (userId === approvedUserId || (recentlyApproved && userId.toString() === recentlyApproved)) {
                  continue;
                }

                const res = await api.get(`/authentication/admin/pending/${userId}/`);
                if (res.data) {
                  setLocalAdminToApprove(res.data);
                  break;
                }
              } catch (err: any) {
                continue;
              }
            }
          }
        } catch (error: any) {
        } finally {
          setFetchingPending(false);
        }
      }
    };

    fetchPendingAdminDetails();
  }, [adminToApprove, localAdminToApprove, notifications, approved, approvedUserId]);

  if (fetchingPending) {
    return (
      <PageLayout title="Admin Approval" subtitle="Review and approve admin details">
        <Card>
          <Alert message="Loading..." description="Checking for pending admin approvals..." type="info" showIcon />
        </Card>
      </PageLayout>
    );
  }

  if (!currentAdminToApprove) {
    return (
      <PageLayout title="Admin Approval" subtitle="Review and approve admin details">
        <Card>
          <Alert message="No Admin to Approve" description="No admin details are currently pending approval." type="info" showIcon />
        </Card>
      </PageLayout>
    );
  }

  if (approved) {
    return (
      <PageLayout title="Admin Approval" subtitle="Review and approve admin details">
        <Card>
          <Alert message="Admin Approved" description="The admin has been approved successfully." type="success" showIcon />
        </Card>
      </PageLayout>
    );
  }

  const handleApprove = async (values?: AdminApprovalData) => {
    setLoading(true);
    try {
      // If values provided, update admin details first
      if (values && editMode) {
        const formData = new FormData();
        Object.keys(values).forEach((key) => {
          if (values[key as keyof AdminApprovalData]) {
            formData.append(key, values[key as keyof AdminApprovalData] as string);
          }
        });
        await api.put(`/authentication/admin/detail/update-by-master/${currentAdminToApprove.user}/`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      // Approve the admin details - backend will send notification automatically
      await api.post(`/authentication/admin/detail/approve/${currentAdminToApprove.user}/`);

      // Track the approved user to prevent re-fetching
      setApprovedUserId(currentAdminToApprove.user);
      setApproved(true);
      // Clear the local admin data to prevent re-display
      setLocalAdminToApprove(null);

      // Store approved user ID in sessionStorage to persist across refreshes
      sessionStorage.setItem('recently_approved_admin', currentAdminToApprove.user.toString());

      // Clear the sessionStorage after 5 minutes to allow re-approval if needed
      setTimeout(() => {
        sessionStorage.removeItem('recently_approved_admin');
      }, 5 * 60 * 1000);

      onAdminApprovalSuccess?.(currentAdminToApprove.user);

      message.success('Admin details approved successfully!');
    } catch (error: any) {
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageLayout
      title="Admin Approval"
      subtitle="Review and approve admin details"
      breadcrumbs={[
        { title: 'Admin Approval' }
      ]}
      actions={
        <Button
          type="primary"
          icon={<CheckOutlined />}
          onClick={() => form.submit()}
          loading={loading}
        >
          Approve Admin
        </Button>
      }
    >
      <Card>
      <Form form={form} layout="vertical" onFinish={handleApprove} initialValues={currentAdminToApprove}>
        <Form.Item label="Username" name="username">
          <Input prefix={<UserOutlined />} disabled />
        </Form.Item>
        <Form.Item label="Name" name="name" rules={[{ pattern: /^[A-Za-z\s]+$/, message: 'Name must contain only letters and spaces' }]}>
          <Input prefix={<UserOutlined />} disabled={!editMode} onKeyPress={(e: React.KeyboardEvent<HTMLInputElement>) => { if (!/[A-Za-z\s]/.test(e.key)) { e.preventDefault(); } }} />
        </Form.Item>
        <Form.Item label="Company Name" name="company_name">
          <Input prefix={<BankOutlined />} disabled />
        </Form.Item>
        <Form.Item label="Registered Official Address" name="registered_address">
          <Input.TextArea rows={3} disabled />
        </Form.Item>
        <Form.Item label="Phone Number" name="phone_number" rules={[{ len: 10, message: 'Must be 10 digits' }]}>
          <Input prefix={<PhoneOutlined />} maxLength={10} disabled={!editMode} />
        </Form.Item>
        <Form.Item label="PAN Number" name="pan_number" rules={[{ pattern: /^[A-Z]{5}[0-9]{4}[A-Z]$/, message: 'Invalid PAN format' }]}>
          <Input disabled={!editMode} />
        </Form.Item>
        <Form.Item label="GST Number" name="gst_number" rules={[{ pattern: /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/, message: 'Invalid GST format' }]}>
          <Input disabled={!editMode} />
        </Form.Item>
        
        {/* Profile Photo Display */}
        {currentAdminToApprove?.photo_url && (
          <Form.Item label="Profile Photo">
            <div style={{ 
              border: '1px solid #d9d9d9', 
              borderRadius: '6px', 
              padding: '8px', 
              display: 'inline-block',
              backgroundColor: '#fafafa'
            }}>
              <img 
                src={currentAdminToApprove.photo_url} 
                alt="Profile Photo" 
                style={{ 
                  maxWidth: '150px', 
                  maxHeight: '150px', 
                  objectFit: 'cover',
                  borderRadius: '4px'
                }}
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                  if (e.currentTarget.parentElement) {
                    e.currentTarget.parentElement.innerHTML = `
                      <div style="color: #ff4d4f; text-align: center; padding: 20px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">📷</div>
                        <div>Photo not found</div>
                      </div>
                    `;
                  }
                }}
              />
            </div>
          </Form.Item>
        )}
        
        {/* Company Logo Display */}
        {currentAdminToApprove?.logo_url && (
          <Form.Item label="Company Logo">
            <div style={{ 
              border: '1px solid #d9d9d9', 
              borderRadius: '6px', 
              padding: '8px', 
              display: 'inline-block',
              backgroundColor: '#fafafa'
            }}>
              <img 
                src={currentAdminToApprove.logo_url} 
                alt="Company Logo" 
                style={{ 
                  maxWidth: '150px', 
                  maxHeight: '150px', 
                  objectFit: 'contain',
                  borderRadius: '4px'
                }}
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                  if (e.currentTarget.parentElement) {
                    e.currentTarget.parentElement.innerHTML = `
                      <div style="color: #ff4d4f; text-align: center; padding: 20px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">🏢</div>
                        <div>Logo not found</div>
                      </div>
                    `;
                  }
                }}
              />
            </div>
          </Form.Item>
        )}
        
        <Form.Item>
          <div style={{ display: 'flex', gap: '8px' }}>
            <Button type="primary" htmlType="submit" icon={<CheckOutlined />} loading={loading} size="large" style={{ flex: 1 }}>
              {editMode ? 'Update & Approve' : 'Approve As Is'}
            </Button>
            <Button
              icon={<CheckOutlined />}
              onClick={() => handleApprove()}
              loading={loading}
              size="large"
              style={{ flex: 1 }}
              disabled={editMode}
            >
              Approve Without Changes
            </Button>
          </div>
        </Form.Item>
      </Form>
    </Card>
    </PageLayout>
  );
};

export default AdminApproval;