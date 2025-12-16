/**
 * Authentication Cleaner Utility
 * Handles clearing expired/invalid tokens and forcing fresh login
 */

import useAuthStore from '../store/authStore';

/**
 * Clear all authentication data from localStorage and store
 */
export const clearAllAuthData = (): void => {
  
  // Clear from localStorage
  const authKeys = [
    'token',
    'refreshToken',
    'username',
    'usertype',
    'django_user_type',
    'userId',
    'projectId',
    'isPasswordResetRequired',
    'lastRefreshTime',
    'tokenExpiry',
    'grade'
  ];
  
  authKeys.forEach(key => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(key);
    }
  });
  
  // Clear from auth store
  useAuthStore.getState().clearToken();
  
};

/**
 * Handle expired token scenario
 */
export const handleExpiredToken = (): void => {
  clearAllAuthData();
  
  // Redirect to login page
  if (typeof window !== 'undefined') {
    window.location.replace('/login');
  }
};

/**
 * Check if current tokens are expired and handle accordingly
 */
export const checkAndHandleTokenExpiry = (): boolean => {
  const { token, tokenExpiry } = useAuthStore.getState();
  
  if (!token) {
    return false;
  }
  
  if (tokenExpiry) {
    const expiryTime = new Date(tokenExpiry).getTime();
    const currentTime = Date.now();
    
    if (currentTime >= expiryTime) {
      handleExpiredToken();
      return true;
    }
  }
  
  return false;
};

/**
 * Force fresh login by clearing all auth data
 */
export const forceFreshLogin = (message?: string): void => {
  if (message) {
  } else {
  }
  
  clearAllAuthData();
  
  // Show a brief message to user if needed
  if (typeof window !== 'undefined' && message) {
    // You can add a toast notification here if needed
  }
  
  // Redirect to login
  if (typeof window !== 'undefined') {
    window.location.replace('/login');
  }
};

export default {
  clearAllAuthData,
  handleExpiredToken,
  checkAndHandleTokenExpiry,
  forceFreshLogin
};
