/**
 * Security Test Component
 * For testing authentication and logout functionality
 * Remove this component in production
 */

import React, { useState } from 'react';
import { Card, Button, Space, Typography, Alert, Divider } from 'antd';
import { useSecureAuth } from '../hooks/useSecureAuth';
import { validateAuthState, performSecureTokenRefresh } from '../utils/authSecurity';
import useAuthStore from '../store/authStore';

const { Title, Text, Paragraph } = Typography;

const SecurityTest: React.FC = () => {
  const [testResults, setTestResults] = useState<string[]>([]);
  const { logout, isLoggingOut, isAuthenticated, user } = useSecureAuth();
  const { token, refreshToken, tokenExpiry } = useAuthStore();

  const addResult = (result: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${result}`]);
  };

  const testAuthValidation = () => {
    const validation = validateAuthState();
    addResult(`Auth Validation: ${validation.isValid ? 'VALID' : 'INVALID'} - ${validation.reason || 'OK'}`);
  };

  const testTokenRefresh = async () => {
    try {
      addResult('Testing token refresh...');
      const newToken = await performSecureTokenRefresh();
      addResult(`Token Refresh: ${newToken ? 'SUCCESS' : 'FAILED'}`);
    } catch (error: any) {
      addResult(`Token Refresh ERROR: ${error.message}`);
    }
  };

  const testSecureLogout = async () => {
    try {
      addResult('Testing secure logout...');
      await logout({ showMessage: false });
      addResult('Secure Logout: SUCCESS');
    } catch (error: any) {
      addResult(`Secure Logout ERROR: ${error.message}`);
    }
  };

  const clearResults = () => {
    setTestResults([]);
  };

  return (
    <Card title="🔒 Authentication Security Test Panel" style={{ margin: '20px' }}>
      <Alert
        message="Development Tool"
        description="This component is for testing authentication security. Remove in production."
        type="warning"
        showIcon
        style={{ marginBottom: '20px' }}
      />

      <Title level={4}>Current Auth State</Title>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Text><strong>Authenticated:</strong> {isAuthenticated ? '✅ Yes' : '❌ No'}</Text>
        <Text><strong>Username:</strong> {user.username || 'None'}</Text>
        <Text><strong>User Type:</strong> {user.usertype || 'None'}</Text>
        <Text><strong>User ID:</strong> {user.userId || 'None'}</Text>
        <Text><strong>Has Token:</strong> {token ? '✅ Yes' : '❌ No'}</Text>
        <Text><strong>Has Refresh Token:</strong> {refreshToken ? '✅ Yes' : '❌ No'}</Text>
        <Text><strong>Token Expiry:</strong> {tokenExpiry || 'Unknown'}</Text>
        <Text><strong>Logging Out:</strong> {isLoggingOut ? '🔄 Yes' : '❌ No'}</Text>
      </Space>

      <Divider />

      <Title level={4}>Security Tests</Title>
      <Space wrap>
        <Button onClick={testAuthValidation}>
          Test Auth Validation
        </Button>
        <Button onClick={testTokenRefresh} disabled={!refreshToken}>
          Test Token Refresh
        </Button>
        <Button 
          onClick={testSecureLogout} 
          loading={isLoggingOut}
          danger
        >
          Test Secure Logout
        </Button>
        <Button onClick={clearResults}>
          Clear Results
        </Button>
      </Space>

      <Divider />

      <Title level={4}>Test Results</Title>
      <div style={{ 
        maxHeight: '300px', 
        overflowY: 'auto', 
        backgroundColor: '#f5f5f5', 
        padding: '10px',
        borderRadius: '4px',
        fontFamily: 'monospace',
        fontSize: '12px'
      }}>
        {testResults.length === 0 ? (
          <Text type="secondary">No test results yet...</Text>
        ) : (
          testResults.map((result, index) => (
            <div key={index}>{result}</div>
          ))
        )}
      </div>

      <Divider />

      <Alert
        message="Security Notes"
        description={
          <ul>
            <li>Always test logout functionality before deployment</li>
            <li>Verify tokens are properly cleared from localStorage</li>
            <li>Check that API calls fail gracefully after logout</li>
            <li>Ensure users are redirected to login page</li>
            <li>Test token refresh behavior</li>
          </ul>
        }
        type="info"
        showIcon
      />
    </Card>
  );
};

export default SecurityTest;
