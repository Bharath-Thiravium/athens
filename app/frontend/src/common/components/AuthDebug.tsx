import React, { useEffect } from 'react';
import useAuthStore from '../store/authStore';
import { extractUserInfoFromToken } from '../utils/jwtUtils';

const AuthDebug: React.FC = () => {
  const authState = useAuthStore();

  useEffect(() => {
    console.log('=== AUTH DEBUG ===');
    console.log('Auth Store State:', {
      token: !!authState.token,
      username: authState.username,
      usertype: authState.usertype,
      django_user_type: authState.django_user_type,
      userId: authState.userId,
      projectId: authState.projectId,
      department: authState.department,
      grade: authState.grade,
      isApproved: authState.isApproved,
      hasSubmittedDetails: authState.hasSubmittedDetails,
      isAuthenticated: authState.isAuthenticated()
    });

    console.log('LocalStorage Values:', {
      token: !!localStorage.getItem('token'),
      username: localStorage.getItem('username'),
      usertype: localStorage.getItem('usertype'),
      django_user_type: localStorage.getItem('django_user_type'),
      userId: localStorage.getItem('userId'),
      projectId: localStorage.getItem('projectId'),
      department: localStorage.getItem('department'),
      grade: localStorage.getItem('grade'),
      isApproved: localStorage.getItem('isApproved'),
      hasSubmittedDetails: localStorage.getItem('hasSubmittedDetails')
    });
    
    // Try to decode token if available
    if (authState.token) {
      const tokenData = extractUserInfoFromToken(authState.token);
      console.log('Token Data:', tokenData);
    }
  }, [authState]);

  return null; // This component doesn't render anything
};

export default AuthDebug;