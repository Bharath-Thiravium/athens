import React from 'react';
import { Navigate } from 'react-router-dom';
import useAuthStore from '@common/store/authStore';

interface RoleBasedRouteProps {
  allowedRoles: string[];
  children: React.ReactElement;
}

const RoleBasedRoute: React.FC<RoleBasedRouteProps> = ({ allowedRoles, children }) => {
  const { usertype, django_user_type, token, isAuthenticated } = useAuthStore();

  const normalizeRole = (role?: string | null) => {
    if (role === 'master' || role === 'MASTER_ADMIN') return 'masteradmin';
    return role;
  };

  // Check if user is authenticated first
  if (!token || !isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  // Check if user has permission based on role
  const hasPermission = () => {
    // Check both usertype and django_user_type
    const userRoles = [normalizeRole(usertype), normalizeRole(django_user_type)].filter(Boolean);
    
    if (userRoles.length === 0) {
      return false;
    }

    // Master admin has access to everything
    if (userRoles.includes('masteradmin')) {
      return true;
    }

    // Check for exact match in either usertype or django_user_type
    for (const role of userRoles) {
      if (allowedRoles.includes(role)) return true;
      
      // Check for contractor roles with numbers (contractor1, contractor2, etc.)
      if (role?.startsWith('contractor') && allowedRoles.includes('contractor')) return true;
      
      // Check for contractoruser variations
      if (role?.startsWith('contractor') && allowedRoles.includes('contractoruser')) return true;
    }

    return false;
  };

  if (!hasPermission()) {
    // If authenticated but wrong role, redirect to dashboard overview
    console.warn('Access denied for route. User roles:', { usertype, django_user_type }, 'Required roles:', allowedRoles);
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

export default RoleBasedRoute;
