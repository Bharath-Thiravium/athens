
// src/features/dashboard/components/Dashboard.tsx

import React, { useState, useEffect } from 'react';
import {
    Layout, Menu, Button, Avatar, Typography, Dropdown, Space,
    Modal, App, Badge, Card, Divider, Tag, Spin, Tooltip
} from 'antd';
import type { MenuProps } from 'antd';
import {
    MenuUnfoldOutlined, MenuFoldOutlined, UserOutlined, DashboardOutlined, ProjectOutlined,
    TeamOutlined, SettingOutlined, LogoutOutlined, BellOutlined, MessageOutlined, BookOutlined,
    ReadOutlined, FileTextOutlined, SafetyOutlined, FormOutlined, PlusOutlined, ClockCircleOutlined,
    BarChartOutlined, SunOutlined, MoonOutlined, DesktopOutlined, AuditOutlined, RocketOutlined,
    ApartmentOutlined, DeleteOutlined, ArrowRightOutlined, CheckCircleOutlined, ExperimentOutlined,
    EyeOutlined, DatabaseOutlined, ExclamationCircleOutlined, QrcodeOutlined
} from '@ant-design/icons';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';
import axios from 'axios';
import useAuthStore from '@common/store/authStore';
import { useApprovalStatus } from '../../../common/hooks/useApprovalStatus';
import { useResponsiveSidebar } from '@common/hooks/useResponsive';

import api from '@common/utils/axiosetup';
import { useNotificationsContext } from '@common/contexts/NotificationsContext';
import { useTheme } from '@common/contexts/ThemeContext';
import type { Notification } from '@common/utils/webSocketNotificationService';
import UserDetail from '@features/user/components/userdetail';
import DashboardOverview from './DashboardOverview';
import { getEnhancedMenuItemsForUser } from '../config/projectMenuConfig';
import { AIBotWidget } from '@features/ai_bot';
import AttendanceSyncIndicator from '../../../shared/offline/AttendanceSyncIndicator';
import { useChatWebSocket } from '@features/chatbox/hooks/useChatWebSocket';
// No need to import ProjectAttendance here anymore, it's handled by the router
// import ProjectAttendance from '@features/project/components/ProjectAttendance';
import AuthDebug from '@common/components/AuthDebug';

type MenuItem = Required<MenuProps>['items'][number];

const { Header, Sider, Content } = Layout;
const { Title, Text, Paragraph } = Typography;

const Dashboard: React.FC = () => {
    const { message } = App.useApp();

    // =============================================================================
    // STATE, HOOKS, AND LOGIC (Your existing code, unchanged)
    // =============================================================================
    const { theme, setTheme, effectiveTheme } = useTheme();
    const { approvalStatus, loading: approvalLoading, needsApproval, hasSubmittedDetails, isApproved, refetch: refetchApprovalStatus } = useApprovalStatus();
    const { 
        collapsed: _collapsed, 
        mobileVisible, 
        toggleSidebar, 
        closeMobileSidebar,
        isMobile,
        isTablet 
    } = useResponsiveSidebar();
    
    // Force sidebar to always be expanded
    const collapsed = false;
    const [pendingUsers, setPendingUsers] = useState<any[]>([]);
    const [userToApprove, setUserToApprove] = useState<any | null>(null);
    const [adminToApprove, setAdminToApprove] = useState<any | null>(null);
    const [companyLogoUrl, setCompanyLogoUrl] = useState<string | null>(null);
    const [companyName, setCompanyName] = useState<string>('YourBrand');
    const [userProfilePicUrl, setUserProfilePicUrl] = useState<string | null>(null);
    const [meetingInvitationModalVisible, setMeetingInvitationModalVisible] = useState(false);
    const [currentMeetingInvitation, setCurrentMeetingInvitation] = useState<{ momId: any; userId: any; title: any; notificationId: any; } | null>(null);
    const [meetingModalLoading, setMeetingModalLoading] = useState(false);
    const [notificationModal, setNotificationModal] = useState<{visible: boolean, notification?: Notification}>({visible: false});
    const [userMobile, setUserMobile] = useState<string>('');
    const [isLoggingOut, setIsLoggingOut] = useState(false);
    const [userDetails, setUserDetails] = useState<{
        name: string;
        employeeId: string;
        designation: string;
        department: string;
        userType: string;
        projectName: string | null;
    } | null>(null);
    const [inductionStatus, setInductionStatus] = useState<{
        hasCompleted: boolean;
        isEPCSafety: boolean;
        isMasterAdmin: boolean;
    } | null>(null);
    const [subscriptionStatus, setSubscriptionStatus] = useState<{
        isTrialing: boolean;
        subscriptionStatus: string;
        tenantId: string | null;
    } | null>(null);
    const [menuItems, setMenuItems] = useState<MenuItem[]>([
        { key: '/dashboard', icon: <DashboardOutlined />, label: 'Dashboard' },
        { key: '/dashboard/analytics', icon: <BarChartOutlined />, label: 'Analytics' },
        { key: '/dashboard/workers', icon: <TeamOutlined />, label: 'Workers' },
        { key: '/dashboard/ptw', icon: <FormOutlined />, label: 'Permits to Work' },
        { key: '/dashboard/incidentmanagement', icon: <SafetyOutlined />, label: 'Incident Management' },
        { key: '/dashboard/inspection', icon: <ExperimentOutlined />, label: 'Inspections' },
        { key: '/dashboard/training', icon: <BookOutlined />, label: 'Training' },
        { key: '/dashboard/manpower', icon: <UserOutlined />, label: 'Manpower' },
    ]);
    const [menuLoading, setMenuLoading] = useState<boolean>(false);

    const { notifications, unreadCount, markAsRead, markAllAsRead, deleteNotification, sendApprovalNotification } = useNotificationsContext();
    const { unreadCounts: chatUnreadCounts } = useChatWebSocket();
    
    // Calculate total chat unread count
    const totalChatUnreadCount = Object.values(chatUnreadCounts || {}).reduce((sum, count) => sum + count, 0);
    const navigate = useNavigate();
    const location = useLocation();
    const { 
        clearToken, 
        username, 
        usertype, 
        django_user_type,
        department,
        grade,
        isApproved: authIsApproved,
        hasSubmittedDetails: authHasSubmittedDetails,
        restoreUserDataFromToken,
        forceTokenSync
    } = useAuthStore();

    // Load menu items based on user type (no API call)
    useEffect(() => {
        let isMounted = true;
        const loadMenu = async () => {
            try {
                setMenuLoading(true);
                const items = await getEnhancedMenuItemsForUser(
                    usertype, 
                    django_user_type, 
                    authIsApproved || isApproved, 
                    authHasSubmittedDetails || hasSubmittedDetails,
                    userDetails?.department || department
                );
                if (isMounted) {
                    setMenuItems(items);
                }
            } catch (error) {
                console.error('Failed to generate menu items:', error);
                if (isMounted) {
                    setMenuItems([
                        { key: '/dashboard', icon: <DashboardOutlined />, label: 'Overview' },
                        { key: '/dashboard/profile', icon: <UserOutlined />, label: 'Profile' },
                    ]);
                }
            } finally {
                if (isMounted) {
                    setMenuLoading(false);
                }
            }
        };
        
        if (usertype || django_user_type) {
            loadMenu();
        }
        
        return () => {
            isMounted = false;
        };
    }, [usertype, django_user_type, authIsApproved, isApproved, authHasSubmittedDetails, hasSubmittedDetails, userDetails?.department, department]);

    // Check induction status on component mount
    useEffect(() => {
        const checkInductionStatus = async () => {
            try {
                const response = await api.get('/authentication/induction-status/');
                setInductionStatus(response.data);
            } catch (error) {
                // Silently handle induction status check failure
                setInductionStatus({ hasCompleted: true, isEPCSafety: false, isMasterAdmin: false });
            }
        };
        
        checkInductionStatus();
    }, []);

    // Check subscription status on component mount
    useEffect(() => {
        const checkSubscriptionStatus = async () => {
            try {
                const response = await api.get('/authentication/tenant-subscription-status/');
                setSubscriptionStatus(response.data);
            } catch (error) {
                // Silently handle subscription status check failure
                setSubscriptionStatus({ isTrialing: false, subscriptionStatus: 'active', tenantId: null });
            }
        };
        
        checkSubscriptionStatus();
    }, []);

    // Check if user needs induction training (should have blurred sidebar)
    const needsInductionTraining = inductionStatus && 
        !inductionStatus.hasCompleted && 
        !inductionStatus.isEPCSafety && 
        !inductionStatus.isMasterAdmin;

    const isProjectScopedUser = ['projectadmin', 'adminuser', 'clientuser', 'epcuser', 'contractoruser'].includes(django_user_type || '')
        || ['client', 'epc', 'contractor'].includes(usertype || '');
    const projectName = userDetails?.projectName || null;
    const showProjectName = Boolean(projectName) && isProjectScopedUser;
    
    // Debug log to check auth store values
    useEffect(() => {
        console.log('Dashboard auth store values:', {
            username,
            usertype,
            django_user_type,
            department,
            grade,
            authIsApproved,
            authHasSubmittedDetails
        });
        
        // Force sync with JWT token data if user types don't match
        if (usertype === 'user' || django_user_type === 'user') {
            console.log('User type is generic "user", forcing token sync...');
            forceTokenSync();
        }
        
        // Try to restore user data from token if missing
        if (!usertype || !django_user_type) {
            console.log('User data missing, attempting to restore from token...');
            restoreUserDataFromToken();
        }
    }, [username, usertype, django_user_type, department, grade, authIsApproved, authHasSubmittedDetails, restoreUserDataFromToken, forceTokenSync]);


    const getSelectedKey = () => location.pathname;
    const [selectedKey, setSelectedKey] = useState<string>(getSelectedKey());
    useEffect(() => { setSelectedKey(getSelectedKey()); }, [location]);

    const handleUserMenuClick = (e: any) => {
        if (e.key === '/dashboard/training/check-in') navigate('/dashboard/training/check-in');
        else if (e.key === '/dashboard/profile') navigate('/dashboard/profile');
        else if (e.key === '/dashboard/settings') navigate('/dashboard/settings');
        else if (e.key === 'logout') handleLogout();
    };

    const handleLogout = async () => {
        try {
          // Set loading state IMMEDIATELY to prevent dashboard flash
          setIsLoggingOut(true);

          // Get tokens before clearing
          const { token, refreshToken } = useAuthStore.getState();

          // IMMEDIATE navigation to prevent unauthorized user flash
          navigate('/login', { replace: true });

          // Make logout API call if we have tokens
          if (token && refreshToken) {
            try {
              await api.post('/authentication/logout/',
                { refresh: refreshToken },
                {
                  headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                  },
                  timeout: 10000
                }
              );
            } catch (apiError: any) {
              // Continue with local logout even if API fails
            }
          }

          // Clear tokens AFTER navigation starts
          clearToken();

          // Show success message
          try {
            message.success('Logged out successfully');
          } catch (msgError) {
            // Message failed to show
          }

        } catch (error) {
          // Fallback: ensure user is logged out locally
          clearToken();
          message.success('Logged out successfully');
          setTimeout(() => {
            navigate('/login', { replace: true });
          }, 100);
        } finally {
          setIsLoggingOut(false);
        }
    };

    const handleMenuClick = (e: any) => {
        console.log('Menu clicked:', e.key, e.keyPath);
        console.log('Current location:', location.pathname);
        console.log('About to navigate to:', e.key);
        
        // Prevent navigation if key is invalid
        if (!e.key || e.key === location.pathname) {
            console.log('Skipping navigation - same path or invalid key');
            return;
        }
        
        // Special handling for inspection reports
        if (e.key === '/dashboard/inspection/reports') {
            console.log('Navigating to inspection reports');
            navigate('/dashboard/inspection/reports');
            return;
        }
        
        // Default navigation with error handling
        try {
            console.log('Executing navigate to:', e.key);
            navigate(e.key);
            console.log('Navigation completed to:', e.key);
        } catch (error) {
            console.error('Navigation error:', error);
        }
    };



    const handleApprovalSuccess = async (approvedUserId: number) => {
        setPendingUsers(pendingUsers.filter((user) => user.id !== approvedUserId));
        setUserToApprove(null);
        try {
          await sendApprovalNotification(approvedUserId, { title: 'Your Details Approved', message: 'Your user details have been approved by the administrator.', formType: 'userdetail', itemId: approvedUserId });
          message.success('User approved successfully and notification sent.');
        } catch (error) {
          message.success('User approved successfully.');
        }
    };

    const handleAdminApprovalSuccess = async (_approvedAdminId: number) => {
        setAdminToApprove(null);
        // Backend already sends notification, no need to send from frontend
        message.success('Admin approved successfully.');
    };

    const handleNotificationClick = async (notification: Notification) => {
        try {
            // Notification clicked - processing

            if (!notification.read) await markAsRead(notification.id);
            setNotificationModal({ visible: true, notification });
            if (notification.type === 'meeting_invitation' && notification.data && typeof notification.data === 'object' && 'momId' in notification.data) {
                setCurrentMeetingInvitation({ momId: notification.data.momId, userId: notification.data.userId, title: notification.data.title || 'a meeting', notificationId: notification.id, });
                setMeetingInvitationModalVisible(true);
            }
        } catch (error) {
            message.error("Could not process notification.");
        }
    };

    const handleMarkAllAsRead = async () => {
        await markAllAsRead();
        message.success('All notifications marked as read');
    };

    const handleMeetingResponse = async (status: 'accepted' | 'rejected') => {
        if (!currentMeetingInvitation) return;
        const { momId, userId } = currentMeetingInvitation;
        setMeetingModalLoading(true);
        try {
            await api.post(`/api/v1/mom/${momId}/participants/${userId}/response/`, { status });
            message.success(`You have ${status} the meeting invitation.`);
            setMeetingInvitationModalVisible(false);
            setCurrentMeetingInvitation(null);
        } catch (err) {
            message.error('Failed to send your response.');
        } finally {
            setMeetingModalLoading(false);
        }
    };

    useEffect(() => {
        const fetchCompanyDetails = async () => {
          try {
            // Use unified endpoint for all user types
            const response = await api.get('/authentication/company-data/');
            console.log('Company data response:', {
              usertype,
              responseSuccess: response.data.success,
              hasLogo: !!response.data.company_logo,
              logoValue: response.data.company_logo
            });

            if (response.data.success) {
              const data = response.data;

              // Update logo with proper URL handling
              if (data.company_logo) {
                let logoUrl = data.company_logo;
                // Always ensure we have the full URL
                if (!logoUrl.startsWith('http')) {
                  logoUrl = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${logoUrl.startsWith('/') ? logoUrl : '/' + logoUrl}`;
                }
                setCompanyLogoUrl(logoUrl);
              } else {
                setCompanyLogoUrl(null);
              }

              // Update company name
              if (data.company_name) {
                setCompanyName(data.company_name);
              } else {
                setCompanyName('YourBrand');
              }
            }
          } catch (error) {
            // Silently handle company data fetch failure
            // Fallback to old endpoints if unified endpoint fails
            try {
              let fallbackResponse;

              if (usertype === 'masteradmin') {
                fallbackResponse = await api.get('/authentication/companydetail/');
              } else {
                fallbackResponse = await api.get('/authentication/admin/me/');
              }

              if (fallbackResponse?.data) {
                const data = fallbackResponse.data;
                let logoUrl = data.company_logo || data.logo_url;
                const companyName = data.company_name;

                if (logoUrl) {
                  // Ensure proper URL format
                  if (!logoUrl.startsWith('http')) {
                    logoUrl = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${logoUrl.startsWith('/') ? logoUrl : '/' + logoUrl}`;
                  }
                  setCompanyLogoUrl(logoUrl);
                }

                if (companyName) {
                  setCompanyName(companyName);
                }
              }
            } catch (fallbackError) {
              // Silently handle fallback fetch failure
            }
          }
        };

        const fetchUserProfilePic = async () => {
          try {
            // Use the new unified profile endpoint
            const profileResponse = await api.get('/authentication/current-user-profile/');
            const profileData = profileResponse.data;
            
            if (profileData) {
              // Set profile picture URL
              if (profileData.profile_picture_url) {
                setUserProfilePicUrl(profileData.profile_picture_url);
              }
              
              // Set user details for display
              setUserDetails({
                name: profileData.name || username || 'User',
                employeeId: profileData.employee_id || 'N/A',
                designation: profileData.designation || 'N/A',
                department: profileData.department || 'N/A',
                userType: ['master', 'MASTER_ADMIN'].includes(profileData.admin_type || profileData.user_type)
                  ? 'masteradmin'
                  : (profileData.admin_type || profileData.user_type || 'N/A'),
                projectName: profileData.project_name || null
              });
            }
          } catch (error) {
            console.error('Failed to fetch user profile:', error);
            // Final fallback - use auth store data
            setUserProfilePicUrl(null);
            setUserDetails({
              name: username || 'User',
              employeeId: 'N/A',
              designation: department || 'N/A',
              department: department || 'N/A',
              userType: django_user_type || usertype || 'N/A',
              projectName: null
            });
          }
        };

        // Only fetch if we have user type information
        if (usertype && username) {
          fetchCompanyDetails();
          fetchUserProfilePic();
        }
      }, [usertype, username, django_user_type]);

    // Separate useEffect for event listeners
    useEffect(() => {
        const handleCompanyDataUpdate = (event: CustomEvent) => {
          if (event.detail) {
            // Update logo if provided
            if (event.detail.logoUrl || event.detail.company_logo) {
              let logoUrl = event.detail.logoUrl || event.detail.company_logo;
              // Ensure proper URL format
              if (!logoUrl.startsWith('http')) {
                logoUrl = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${logoUrl.startsWith('/') ? logoUrl : '/' + logoUrl}`;
              }
              setCompanyLogoUrl(logoUrl);
            }

            // Update company name if provided
            if (event.detail.companyName || event.detail.company_name) {
              const companyName = event.detail.companyName || event.detail.company_name;
              setCompanyName(companyName);
            }
          }
        };

        // Listen for all company data update events
        const eventTypes = [
          'company_logo_updated',
          'company_name_updated',
          'admin_logo_updated',
          'admin_company_updated',
          'company_data_updated'
        ];

        eventTypes.forEach(eventType => {
          window.addEventListener(eventType, handleCompanyDataUpdate as EventListener);
        });

        return () => {
          eventTypes.forEach(eventType => {
            window.removeEventListener(eventType, handleCompanyDataUpdate as EventListener);
          });
        };
    }, []);

    useEffect(() => {
        // Periodically refresh access token safely
        const refreshTokenFunc = async () => {
            try {
                const mod = await import('@common/utils/tokenrefresh');
                const doRefresh = mod.default;
                await doRefresh();
            } catch (err) {
                console.error('Token refresh failed:', err);
            }
        };

        refreshTokenFunc();
        const interval = setInterval(refreshTokenFunc, 10 * 60 * 1000); // every 10 minutes
        return () => clearInterval(interval);
    }, []);

    // Removed fetchUserData call as function was not defined

    // Show loading overlay during logout to prevent flash
    if (isLoggingOut) {
        return (
            <div className="fixed inset-0 bg-white dark:bg-gray-900 flex items-center justify-center z-50">
                <div className="text-center">
                    <Spin size="large" />
                    <div className="mt-4 text-lg text-gray-600 dark:text-gray-300">Logging out...</div>
                </div>
            </div>
        );
    }

    // Show loading screen during logout to prevent unauthorized flash
    if (isLoggingOut) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-color-bg-base">
                <div className="text-center">
                    <Spin size="large" />
                    <div className="mt-4 text-color-text-base">Logging out...</div>
                </div>
            </div>
        );
    }

    return (
        <Layout className="dashboard-layout !bg-color-bg-base">
            <AuthDebug />
            {/* Mobile/Tablet Overlay */}
            {(isMobile || isTablet) && mobileVisible && (
                <div 
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: 'rgba(0, 0, 0, 0.5)',
                        zIndex: 999
                    }}
                    onClick={closeMobileSidebar}
                />
            )}
            
            <div
                className="premium-sidebar"
                style={{ 
                    position: 'fixed',
                    top: 0,
                    left: (isMobile || isTablet) ? (mobileVisible ? 0 : -280) : 0,
                    bottom: 0,
                    width: (isMobile || isTablet) ? 300 : (collapsed ? 80 : 300),
                    minWidth: (isMobile || isTablet) ? 300 : (collapsed ? 80 : 300),
                    zIndex: (isMobile || isTablet) ? 1001 : 50,
                    display: 'flex',
                    flexDirection: 'column',
                    height: '100vh',
                    overflow: 'hidden',
                    transition: 'all 0.3s ease'
                }}
            >
                <div className="sidebar-header" style={{ 
                    justifyContent: collapsed && !(isMobile || isTablet) ? 'center' : 'space-between', 
                    padding: collapsed && !(isMobile || isTablet) ? '16px 8px' : '16px 24px'
                }}>
                    {collapsed && !(isMobile || isTablet) ? (
                        <div style={{ width: 40, height: 40, backgroundColor: '#f0f0f0', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
                            {companyLogoUrl ? (
                                <img 
                                    src={companyLogoUrl} 
                                    alt="Company Logo" 
                                    style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                                    onError={(e) => {
                                        e.currentTarget.style.display = 'none';
                                        e.currentTarget.nextElementSibling.style.display = 'flex';
                                    }}
                                />
                            ) : null}
                            <ApartmentOutlined style={{ fontSize: 20, color: '#666', display: companyLogoUrl ? 'none' : 'block' }} />
                        </div>
                    ) : (
                        <>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <div style={{ width: 40, height: 40, backgroundColor: '#f0f0f0', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
                                    {companyLogoUrl ? (
                                        <img 
                                            src={companyLogoUrl} 
                                            alt="Company Logo" 
                                            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                                            onError={(e) => {
                                                e.currentTarget.style.display = 'none';
                                                e.currentTarget.nextElementSibling.style.display = 'block';
                                            }}
                                        />
                                    ) : null}
                                    <ApartmentOutlined style={{ fontSize: 20, color: '#666', display: companyLogoUrl ? 'none' : 'block' }} />
                                </div>
                                <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.2 }}>
                                    <span style={{ fontWeight: 600, fontSize: 16 }}>{companyName}</span>
                                    {showProjectName && (
                                        <span style={{ fontSize: 12, color: '#6b7280' }}>
                                            Project: {projectName}
                                        </span>
                                    )}
                                </div>
                            </div>
                            {(isMobile || isTablet) && (
                                <Button 
                                    type="text" 
                                    icon={<MenuFoldOutlined />} 
                                    onClick={closeMobileSidebar}
                                    style={{ padding: 8 }}
                                />
                            )}
                        </>
                    )}
                </div>
                <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', minHeight: 0, position: 'relative' }}>
                    <div className={collapsed && !(isMobile || isTablet) ? "p-1" : "p-3"} style={{
                        filter: needsInductionTraining ? 'blur(3px)' : 'none',
                        pointerEvents: needsInductionTraining ? 'none' : 'auto',
                        opacity: needsInductionTraining ? 0.5 : 1,
                        transition: 'all 0.3s ease'
                    }}>
                        <Spin spinning={menuLoading} size="small">
                            <Menu
                                mode="inline"
                                selectedKeys={[selectedKey]}
                                defaultOpenKeys={['category-dashboard', 'category-safety', 'category-training', 'category-workforce', 'category-communication']}
                                onClick={handleMenuClick}
                                className="premium-menu"
                                items={menuItems.map(item => {
                                    // Add notification badge to Chatbox menu item
                                    if (item.key === '/dashboard/chatbox') {
                                        return {
                                            ...item,
                                            label: (
                                                <div className="menu-item-badge">
                                                    {item.label}
                                                    {totalChatUnreadCount > 0 && (
                                                        <span className="notification-badge">{totalChatUnreadCount}</span>
                                                    )}
                                                </div>
                                            )
                                        };
                                    }
                                    return item;
                                })}
                                style={{ height: 'auto', borderRight: 0 }}
                                inlineCollapsed={collapsed && !(isMobile || isTablet)}
                            />
                        </Spin>
                    </div>
                    {needsInductionTraining && (
                        <div style={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            textAlign: 'center',
                            padding: '20px',
                            backgroundColor: 'rgba(255, 255, 255, 0.95)',
                            borderRadius: '8px',
                            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                            zIndex: 10,
                            maxWidth: '200px'
                        }}>
                            <ExclamationCircleOutlined style={{ fontSize: '24px', color: '#faad14', marginBottom: '8px' }} />
                            <div style={{ fontSize: '12px', color: '#666', lineHeight: '1.4' }}>
                                Complete induction training to access menu
                            </div>
                        </div>
                    )}
                </div>
                {!(isMobile || isTablet) && !collapsed && subscriptionStatus?.isTrialing && (
                    <div style={{ padding: 16, flexShrink: 0 }}>
                        <Button
                            block
                            size="large"
                            type="primary"
                            icon={<RocketOutlined />}
                            style={{
                                fontWeight: 600,
                                background: 'linear-gradient(90deg, var(--gradient-start), var(--gradient-end))',
                                border: 'none'
                            }}
                        >
                            Activate Pro Version
                        </Button>
                    </div>
                )}
            </div>
            <Layout className="!bg-transparent transition-all duration-300 h-screen flex flex-col" style={{ 
                marginLeft: (isMobile || isTablet) ? 0 : (collapsed ? 80 : 300)
            }}>
                <Header className="dashboard-header !px-6 flex justify-between items-center !bg-color-bg-base !border-b !border-color-border" style={{ 
                    left: (isMobile || isTablet) ? 0 : (collapsed ? 80 : 300)
                }}>
                <div> <Button type="text" icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />} onClick={toggleSidebar} className="!h-10 !w-10 !text-xl !text-color-text-muted" /> </div>
                
                <div className="flex items-center gap-4">
                    {/* User Info */}
                    <div className="hidden md:flex items-center gap-3 px-3 py-2 bg-color-ui-base rounded-lg border border-color-border">
                        <Avatar 
                            size={32}
                            src={userProfilePicUrl} 
                            icon={<UserOutlined />}
                        />
                        <div>
                            <Tooltip 
                                title={
                                    <div>
                                        <div><strong>Employee ID:</strong> {userDetails?.employeeId || 'N/A'}</div>
                                        <div><strong>Designation:</strong> {userDetails?.designation || 'N/A'}</div>
                                        <div><strong>Department:</strong> {userDetails?.department || 'N/A'}</div>
                                        <div><strong>User Type:</strong> {userDetails?.userType || django_user_type || usertype || 'N/A'}</div>
                                    </div>
                                }
                                placement="bottom"
                            >
                                <Text className="font-semibold text-color-text-base cursor-pointer block text-sm">
                                    {userDetails?.name || username || 'User'}
                                </Text>
                            </Tooltip>
                            <Text className="text-xs text-color-text-muted block">
                                {userDetails?.designation || userDetails?.userType || django_user_type || usertype || 'N/A'}
                            </Text>
                        </div>
                    </div>
                    
                    {/* Theme Toggle */}
                    <div className="flex items-center bg-color-ui-base p-1 rounded-full shadow-inner">
                        <Button shape="circle" size="small" icon={<SunOutlined />} onClick={() => setTheme('light')} className={effectiveTheme === 'light' ? '!bg-color-primary !text-white' : '!bg-transparent !border-none !text-color-text-muted'} />
                        <Button shape="circle" size="small" icon={<MoonOutlined />} onClick={() => setTheme('dark')} className={effectiveTheme === 'dark' ? '!bg-color-primary !text-white' : '!bg-transparent !border-none !text-color-text-muted'} />
                    </div>

                    <AttendanceSyncIndicator />
                    
                    {/* Notifications */}
                    <Dropdown popupRender={() => (
                        <Card className="w-80" bodyStyle={{ padding: 0 }}>
                            <div className="p-4 flex items-center justify-between border-b border-color-border"> <Text strong className="text-color-text-base">Notifications</Text> {unreadCount > 0 && <Button type="link" size="small" onClick={handleMarkAllAsRead}>Mark all as read</Button>} </div>
                            <div className="max-h-96 overflow-y-auto p-2 space-y-1">
                                {notifications.length > 0 ? (
                                    notifications.map(n => (
                                        <div key={n.id} onClick={() => handleNotificationClick(n)} className={`p-3 rounded-lg cursor-pointer transition-colors ${!n.read ? 'bg-color-primary/10' : 'hover:bg-color-ui-hover'}`}>
                                            <Space align="start">
                                                <Avatar icon={<UserOutlined />} className={!n.read ? '!bg-color-primary text-white' : ''} />
                                                <div> <Text strong className="block truncate text-color-text-base">{n.title}</Text> <Text className="text-xs line-clamp-2 text-color-text-muted">{n.message}</Text> </div>
                                                {!n.read && <div className="mt-1 w-2 h-2 bg-color-primary rounded-full flex-shrink-0" />}
                                            </Space>
                                        </div>
                                    ))
                                ) : ( <div className="text-center py-8 text-color-text-muted"><BellOutlined className="text-3xl mb-2 opacity-50" /><p>No new notifications</p></div> )}
                            </div>
                        </Card>
                     )} placement="bottomRight" arrow trigger={['click']}>
                        <Button shape="circle" icon={<Badge count={unreadCount} size="small"><BellOutlined /></Badge>} size="large" type="text" className="!text-color-text-muted" />
                    </Dropdown>
                    
                    {/* Profile Dropdown */}
                    <Dropdown menu={{ 
                        onClick: handleUserMenuClick, 
                        items: [
                            {
                                key: '/dashboard/training/check-in',
                                label: 'Training Check-in',
                                icon: <QrcodeOutlined />
                            },
                            // Only show Profile Settings for non-master users
                            ...(django_user_type !== 'masteradmin' && usertype !== 'masteradmin' ? [{
                                key: '/dashboard/profile',
                                label: 'Profile Settings',
                                icon: <UserOutlined />
                            }] : []),
                            ...(usertype === 'masteradmin' ? [{
                                key: '/dashboard/settings',
                                label: 'Company Settings',
                                icon: <SettingOutlined />
                            }] : []),
                            {
                                type: 'divider'
                            },
                            {
                                key: 'logout',
                                label: 'Logout',
                                icon: <LogoutOutlined />,
                                danger: true
                            }
                        ]
                    }} placement="bottomRight" arrow trigger={['click']} >
                        <Avatar 
                            size="large" 
                            src={userProfilePicUrl} 
                            icon={<UserOutlined />} 
                            className="cursor-pointer"
                            style={{ backgroundColor: userProfilePicUrl ? 'transparent' : undefined }}
                        />
                    </Dropdown>
                </div>
            </Header>

           <Content className="dashboard-content">
                 {/* Approval Status Banner - Compact */}
                 {needsApproval && (
                     <div className="approval-banner" style={{
                         backgroundColor: hasSubmittedDetails ? '#fff7e6' : '#fff2f0',
                         borderBottom: `1px solid ${hasSubmittedDetails ? '#ffd591' : '#ffccc7'}`,
                         padding: '8px 24px',
                         minHeight: 'auto'
                     }}>
                         <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
                             <div style={{
                                 width: '6px',
                                 height: '6px',
                                 borderRadius: '50%',
                                 backgroundColor: hasSubmittedDetails ? '#fa8c16' : '#f5222d',
                                 flexShrink: 0
                             }} />
                             <Text style={{ color: hasSubmittedDetails ? '#d48806' : '#cf1322', fontSize: '13px', lineHeight: '1.2' }}>
                                 {hasSubmittedDetails
                                     ? 'Details pending approval'
                                     : 'Complete profile to access all features'
                                 }
                             </Text>
                             {!hasSubmittedDetails && (
                                 <Button
                                     type="primary"
                                     size="small"
                                     style={{ fontSize: '12px', height: '24px', padding: '0 8px' }}
                                     onClick={() => {
                                         console.log('Complete Profile clicked:', {
                                             django_user_type,
                                             usertype,
                                             hasSubmittedDetails,
                                             isApproved
                                         });
                                         
                                         if (django_user_type === 'projectadmin') {
                                             navigate('/dashboard/admindetail');
                                         } else if (django_user_type === 'adminuser') {
                                             navigate('/dashboard/userdetail');
                                         } else {
                                             // Fallback for other user types
                                             navigate('/dashboard/profile');
                                         }
                                     }}
                                 >
                                     Complete Profile
                                 </Button>
                             )}
                         </div>
                     </div>
                 )}

                 <div className="dashboard-content-wrapper" style={{ 
                     flex: 1, 
                     overflow: 'auto',
                     padding: '16px',
                     minHeight: 0
                 }}>
                     {location.pathname === '/dashboard' ? (
                        <DashboardOverview />
                      ) : location.pathname === '/dashboard/profile' && django_user_type === 'adminuser' ? (
                        <UserDetail initialMobile={userMobile} />
                      ) : (
                        <Outlet context={{ userToApprove, onApprovalSuccess: handleApprovalSuccess, adminToApprove, onAdminApprovalSuccess: handleAdminApprovalSuccess }} />
                      )}
                 </div>
            </Content>
                {currentMeetingInvitation && ( <Modal title="Meeting Invitation" open={meetingInvitationModalVisible} onCancel={() => setMeetingInvitationModalVisible(false)} footer={[ <Button key="reject" danger onClick={() => handleMeetingResponse('rejected')} loading={meetingModalLoading}>Reject</Button>, <Button key="accept" type="primary" onClick={() => handleMeetingResponse('accepted')} loading={meetingModalLoading}>Accept</Button> ]} > <p>You have been invited to a meeting titled: <strong>{currentMeetingInvitation.title}</strong>.</p> <Text type="secondary">Do you want to accept or reject the invitation?</Text> </Modal> )}
                {notificationModal.visible && notificationModal.notification && (
                    <Modal open={notificationModal.visible} onCancel={() => setNotificationModal({visible: false})} title={<><BellOutlined /> Notification Details</>}
                      footer={[
                          <Button key="delete" danger icon={<DeleteOutlined />} onClick={async () => { if (notificationModal.notification) { await deleteNotification(notificationModal.notification.id); setNotificationModal({visible: false}); message.success('Notification deleted'); } }}>Delete</Button>,
                          (() => {
                            const hasLink = !!notificationModal.notification.link;
                            const isUserDetail = notificationModal.notification.data?.formType === 'userdetail' && django_user_type === 'projectadmin';
                            const isAdminDetail = notificationModal.notification.data?.formType === 'admindetail' && usertype === 'masteradmin';


                            const showButton = hasLink || isUserDetail || isAdminDetail;



                            return showButton;
                          })() && (
                              <Button key="view" type="primary" icon={<ArrowRightOutlined />} onClick={async () => {
                                  const notif = notificationModal.notification;
                                  if (!notif) return;

                                  // Process notification click

                                  // Check auth state

                                  // Prepare auth state for navigation

                                  setNotificationModal({visible: false});
                                  if (notif.data?.formType === 'userdetail' && django_user_type === 'projectadmin') {
                                    try {
                                        const userId = notif.data?.user_id || notif.data?.userId;
                                        const res = await api.get(`/authentication/userdetail/pending/${userId}/`);
                                        if (res.data) {
                                            setUserToApprove(res.data);
                                            navigate('/dashboard/profile');
                                        } else { message.info('User details no longer pending or could not be found.'); }
                                    } catch { message.error('Failed to load user details for approval.'); }
                                  } else if (notif.data?.formType === 'admindetail' && usertype === 'masteradmin') {
                                    try {
                                        // Use the correct user ID from notification data
                                        const userId = notif.data?.user_id || notif.data?.userId;
                                        console.log('Fetching admin details for user ID:', userId, 'from notification:', notif.data);
                                        
                                        const res = await api.get(`/authentication/admin/pending/${userId}/`);
                                        if (res.data) {
                                            console.log('Admin details fetched successfully:', res.data);
                                            // Store the admin data for approval in AdminDetail component
                                            setAdminToApprove(res.data);

                                            // Also store in sessionStorage as backup
                                            sessionStorage.setItem('adminToApprove', JSON.stringify(res.data));

                                            // Small delay to ensure state is updated before navigation
                                            setTimeout(() => {
                                                navigate('/dashboard/admindetail');
                                            }, 100);
                                        } else {
                                            message.info('Admin details no longer pending or could not be found.');
                                        }
                                    } catch (error: any) {
                                        console.error('Error fetching admin details:', error);
                                        if (error.response?.status === 404) {
                                            const errorMsg = error.response?.data?.error || 'Admin details not found';
                                            if (errorMsg.includes('already approved')) {
                                                message.info('These admin details have already been approved.');
                                            } else if (errorMsg.includes('No admin details found')) {
                                                message.info('No admin details submitted for approval yet.');
                                            } else {
                                                message.info('Admin details no longer pending approval.');
                                            }
                                        } else {
                                            message.error('Failed to load admin details for approval.');
                                        }
                                    }
                                  } else if (notif.link) {
                                      const authState = useAuthStore.getState();
                                      console.log('Auth state for link navigation:', {
                                        token: !!authState.token,
                                        usertype: authState.usertype,
                                        userId: authState.userId,
                                        isAuthenticated: authState.isAuthenticated(),
                                        tokenExpiry: authState.tokenExpiry
                                      });

                                      // Check authentication before navigation
                                      if (!authState.token || !authState.isAuthenticated()) {
                                        message.error('Please log in again to view this content.');
                                        return;
                                      }

                                      // Add a small delay to ensure modal is closed and state is stable
                                      setTimeout(() => {
                                        const currentAuthState = useAuthStore.getState();
                                        console.log('Current auth state after timeout:', {
                                          token: !!currentAuthState.token,
                                          usertype: currentAuthState.usertype,
                                          userId: currentAuthState.userId,
                                          isAuthenticated: currentAuthState.isAuthenticated()
                                        });

                                        // Double-check authentication after timeout
                                        if (currentAuthState.token && currentAuthState.isAuthenticated() && notif.link) {
                                          navigate(notif.link);
                                        } else {
                                          message.error('Authentication expired. Please log in again.');
                                        }
                                      }, 200);
                                  }
                              }}>View Details</Button>
                          ),

                          <Button key="close" onClick={() => setNotificationModal({visible: false})}>Close</Button>
                      ]}
                    >
                        <Title level={5}>{notificationModal.notification.title}</Title>
                        <Paragraph>{notificationModal.notification.message}</Paragraph>
                        <Divider style={{margin: '12px 0'}} />
                        <Text type="secondary"> <ClockCircleOutlined style={{marginRight: 8}}/> {new Date(notificationModal.notification.created_at).toLocaleString()} </Text>
                        {!notificationModal.notification.read && ( <Tag color="blue" style={{ marginLeft: 12 }}>New</Tag> )}
                    </Modal>
                )}
            </Layout>
            {/* AI Bot Widget - Floating */}
            <AIBotWidget />
        </Layout>
    );
};

export default Dashboard;
