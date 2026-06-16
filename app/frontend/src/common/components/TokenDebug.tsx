import React, { useEffect, useState } from 'react';
import useAuthStore from '../store/authStore';
import api from '../utils/axiosetup';

const TokenDebug: React.FC = () => {
  const [debugInfo, setDebugInfo] = useState<any>({});
  const authState = useAuthStore();

  useEffect(() => {
    const checkTokenAndFetch = async () => {
      const storedToken = localStorage.getItem('token');
      const authToken = authState.token;
      
      const info = {
        authStoreToken: authToken,
        localStorageToken: storedToken,
        tokenType: typeof authToken,
        isValidJWT: authToken && typeof authToken === 'string' && authToken.includes('.'),
        username: authState.username,
        usertype: authState.usertype,
        projectId: authState.projectId
      };
      
      setDebugInfo(info);
      console.log('Token Debug Info:', info);
      
      // Force API calls if we have user data but invalid token
      if (authState.username && authState.usertype && (!authToken || authToken === 'true')) {
        console.log('Forcing API calls with invalid token...');
        
        try {
          // Try company data
          const companyResponse = await api.get('/authentication/company-data/');
          console.log('Forced company data response:', companyResponse.data);
        } catch (error) {
          console.error('Forced company data error:', error);
        }
        
        try {
          // Try profile data
          const profileResponse = await api.get('/authentication/current-user-profile/');
          console.log('Forced profile response:', profileResponse.data);
        } catch (error) {
          console.error('Forced profile error:', error);
        }
      }
    };
    
    checkTokenAndFetch();
  }, [authState.token, authState.username, authState.usertype]);

  return (
    <div style={{ 
      position: 'fixed', 
      top: 10, 
      right: 10, 
      background: 'rgba(0,0,0,0.8)', 
      color: 'white', 
      padding: '10px', 
      fontSize: '12px',
      zIndex: 9999,
      maxWidth: '300px'
    }}>
      <div><strong>Token Debug:</strong></div>
      <div>Auth Token: {String(debugInfo.authStoreToken)}</div>
      <div>LS Token: {String(debugInfo.localStorageToken)}</div>
      <div>Type: {debugInfo.tokenType}</div>
      <div>Valid JWT: {String(debugInfo.isValidJWT)}</div>
      <div>Username: {debugInfo.username}</div>
      <div>User Type: {debugInfo.usertype}</div>
    </div>
  );
};

export default TokenDebug;