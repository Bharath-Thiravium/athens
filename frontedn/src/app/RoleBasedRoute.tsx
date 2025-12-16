import React from 'react';
import { Navigate } from 'react-router-dom';
import useAuthStore from '@common/store/authStore';

interface RoleBasedRouteProps {
  allowedRoles: string[];
  children: React.ReactElement;
}

const RoleBasedRoute: React.FC<RoleBasedRouteProps> = ({ allowedRoles, children }) => {
  const { usertype, token, isAuthenticated, tokenExpiry } = useAuthStore();

  // Check if user is authenticated first
  if (!token || !isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  // Check if user has permission based on role
  const hasPermission = () => {
    if (!usertype) {
      return false;
    }

    // Check for exact match first
    if (allowedRoles.includes(usertype)) return true;

    // Check for contractor roles with numbers (contractor1, contractor2, etc.)
    if (usertype.startsWith('contractor') && allowedRoles.includes('contractor')) return true;

    // Check for contractoruser variations
    if (usertype.startsWith('contractor') && allowedRoles.includes('contractoruser')) return true;

    return false;
  };

  if (!hasPermission()) {
    // If authenticated but wrong role, redirect to dashboard overview
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

export default RoleBasedRoute;
