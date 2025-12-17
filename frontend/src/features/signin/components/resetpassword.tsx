import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Typography, App } from 'antd';
import api from '@common/utils/axiosetup';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '@common/store/authStore';

const { Title } = Typography;

const ResetPassword: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { message } = App.useApp();

  const setIsPasswordResetRequired = useAuthStore((state) => state.setIsPasswordResetRequired);
  const username = useAuthStore((state) => state.username);
  const userId = useAuthStore((state) => state.userId) as string | number | null;
  const djangoUserType = useAuthStore((state) => state.django_user_type);

  useEffect(() => {
    if (!useAuthStore.getState().isAuthenticated()) {
      navigate('/login');
    }
  }, [navigate]);

  const onFinish = async (values: any) => {
    if (values.newPassword !== values.confirmPassword) {
      message.error('New password and confirm password do not match');
      return;
    }

    setLoading(true);
    try {
      if (djangoUserType === 'projectadmin') {
        // Project admin self-reset
        await api.put('/authentication/admin/reset-password/', {
          username, // Include username for projectadmin
          new_password: values.newPassword, // Use new_password to match AdminCreation.tsx
        });
      } else if (djangoUserType === 'adminuser' && userId) {
        // Admin user self-reset (must use userId, not username)
        await api.put(`/authentication/projectadminuser/reset-password/${userId}/`, {
          password: values.newPassword, // This endpoint uses password instead of new_password
        });
      } else {
        message.error('User type not supported for password reset.');
        setLoading(false);
        return;
      }

      message.success('Password reset successful. Please log in with your new password.');
      setIsPasswordResetRequired(false);
      useAuthStore.getState().clearToken();
      navigate('/login');
    } catch (error) {
      message.error('Failed to reset password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: 'auto', padding: '40px 20px' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 24 }}>
        Set New Password
      </Title>
      <p style={{ textAlign: 'center', marginBottom: 24 }}>
        You need to set a new password before continuing.
      </p>

      <Form layout="vertical" onFinish={onFinish} size="large">
        <Form.Item
          label="New Password"
          name="newPassword"
          rules={[
            { required: true, message: 'Please input your new password!' },
            { min: 8, message: 'Password must be at least 8 characters long' },
            {
              pattern: /[A-Z]/,
              message: 'Password must contain at least one uppercase letter',
            },
            {
              pattern: /[0-9]/,
              message: 'Password must contain at least one number',
            },
            {
              pattern: /[!@#$%^&*(),.?":{}|<>]/,
              message: 'Password must contain at least one special character',
            },
          ]}
        >
          <Input.Password placeholder="Enter your new password" />
        </Form.Item>

        <Form.Item
          label="Confirm New Password"
          name="confirmPassword"
          dependencies={['newPassword']}
          rules={[
            { required: true, message: 'Please confirm your new password!' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('newPassword') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('The two passwords do not match!'));
              },
            }),
          ]}
        >
          <Input.Password placeholder="Confirm your new password" />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" block loading={loading}>
            Set Password
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default ResetPassword;
