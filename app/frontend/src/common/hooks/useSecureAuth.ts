/**
 * Secure Authentication Hook
 * Provides consistent authentication and logout functionality across the app
 */

import { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { App } from 'antd';
import useAuthStore from '../store/authStore';
import { performSecureLogout, validateAuthState, LogoutOptions } from '../utils/authSecurity';

export interface UseSecureAuthReturn {
  isLoggingOut: boolean;
  logout: (options?: LogoutOptions) => Promise<void>;
  isAuthenticated: boolean;
  user: {
    username: string | null;
    usertype: string | null;
    userId: string | number | null;
  };
  validateAuth: () => boolean;
}

/**
 * Hook for secure authentication management
 */
export const useSecureAuth = (): UseSecureAuthReturn => {
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const navigate = useNavigate();
  const { message } = App.useApp();
  
  const { 
    token, 
    username, 
    usertype, 
    userId, 
    isAuthenticated: storeIsAuthenticated 
  } = useAuthStore();

  /**
   * Secure logout function
   */
  const logout = useCallback(async (options: LogoutOptions = {}) => {
    if (isLoggingOut) {
      return;
    }

    try {
      setIsLoggingOut(true);

      // Use the secure logout utility
      const result = await performSecureLogout({
        redirectTo: options.redirectTo || '/login',
        showMessage: false, // We'll handle the message here
        ...options
      });

      // Show success message if logout was successful and not silent
      if (result.success && options.showMessage !== false) {
        message.success('Logged out successfully');
      }

      // Navigate if not redirecting automatically
      if (!options.redirectTo) {
        navigate('/login', { replace: true });
      }

    } catch (error) {
      
      // Fallback: clear tokens and redirect
      useAuthStore.getState().clearToken();
      navigate('/login', { replace: true });
      
      if (options.showMessage !== false) {
        message.success('Logged out successfully');
      }
    } finally {
      setIsLoggingOut(false);
    }
  }, [isLoggingOut, navigate, message]);

  /**
   * Validate current authentication state
   */
  const validateAuth = useCallback((): boolean => {
    const validation = validateAuthState();
    
    if (!validation.isValid && validation.shouldRedirect) {
      logout({ silent: true, showMessage: false });
      return false;
    }
    
    return validation.isValid;
  }, [logout]);

  /**
   * Check authentication on mount and token changes
   */
  useEffect(() => {
    if (token) {
      validateAuth();
    }
  }, [token, validateAuth]);

  return {
    isLoggingOut,
    logout,
    isAuthenticated: storeIsAuthenticated(),
    user: {
      username,
      usertype,
      userId
    },
    validateAuth
  };
};

/**
 * Hook for logout functionality only (lighter version)
 */
export const useLogout = () => {
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const navigate = useNavigate();

  const logout = useCallback(async (options: LogoutOptions = {}) => {
    if (isLoggingOut) return;

    try {
      setIsLoggingOut(true);
      const result = await performSecureLogout({
        redirectTo: options.redirectTo || '/login',
        showMessage: false, // Handle message here
        ...options
      });

      // Show success message if logout was successful and not silent
      if (result.success && options.showMessage !== false) {
        // Import message dynamically to avoid issues
        try {
          const { message } = await import('antd');
          message.success('Logged out successfully');
        } catch {
        }
      }

      if (!options.redirectTo) {
        navigate('/login', { replace: true });
      }
    } catch (error) {
      useAuthStore.getState().clearToken();
      navigate('/login', { replace: true });
    } finally {
      setIsLoggingOut(false);
    }
  }, [isLoggingOut, navigate]);

  return { logout, isLoggingOut };
};

export default useSecureAuth;
