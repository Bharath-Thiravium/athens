import { useState, useEffect } from 'react';
import useAuthStore from '../store/authStore';
import api from '../utils/axiosetup';

interface ApprovalStatus {
  has_submitted_details: boolean;
  is_approved: boolean;
  user_type: string;
  django_user_type: string;
  requires_approval: boolean;
}

export const useApprovalStatus = () => {
  const [approvalStatus, setApprovalStatus] = useState<ApprovalStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token, django_user_type, usertype, setApprovalStatus: setAuthApprovalStatus } = useAuthStore();

  const fetchApprovalStatus = async () => {
    if (!token || !django_user_type) {
      setLoading(false);
      return;
    }

    // Exempt master users from approval/detail requirements entirely
    if (usertype === 'master') {
      setApprovalStatus({
        has_submitted_details: true,
        is_approved: true,
        user_type: django_user_type,
        django_user_type: django_user_type,
        requires_approval: false
      });
      // Also sync to auth store so menus and other consumers see full access
      setAuthApprovalStatus(true, true);
      setLoading(false);
      return;
    }

    // Only check approval status for users who need approval
    if (!['projectadmin', 'adminuser'].includes(django_user_type)) {
      setApprovalStatus({
        has_submitted_details: true,
        is_approved: true,
        user_type: django_user_type,
        django_user_type: django_user_type,
        requires_approval: false
      });
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await api.get('/authentication/approval/status/');
      const status = response.data;
      
      setApprovalStatus(status);
      
      // Update auth store with approval status
      setAuthApprovalStatus(status.is_approved, status.has_submitted_details);
      
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to fetch approval status');
      // Default to requiring approval if we can't fetch status
      setApprovalStatus({
        has_submitted_details: false,
        is_approved: false,
        user_type: django_user_type,
        django_user_type: django_user_type,
        requires_approval: true
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovalStatus();
  }, [token, django_user_type]);

  const refetch = () => {
    fetchApprovalStatus();
  };

  return {
    approvalStatus,
    loading,
    error,
    refetch,
    needsApproval: approvalStatus?.requires_approval && !approvalStatus?.is_approved,
    hasSubmittedDetails: approvalStatus?.has_submitted_details || false,
    isApproved: approvalStatus?.is_approved || false
  };
};
