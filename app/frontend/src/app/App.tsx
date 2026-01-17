// src/app/App.tsx

import React, { useEffect, Suspense } from 'react';
import { useNavigate, Routes, Route, useLocation, useOutletContext, Navigate, useParams } from 'react-router-dom';
import { Spin } from 'antd';

import useAuthStore from '@common/store/authStore';
import { ensureCsrfToken } from '@common/utils/axiosetup';

import ErrorBoundary from '@common/components/ErrorBoundary';
import { NotificationsProvider } from '@common/contexts/NotificationsContext';

// --- Page and component imports ---
import SigninApp from '@features/signin/pages/App';
import ResetPassword from '@features/signin/components/resetpassword';

const Dashboard = React.lazy(() => import('@features/dashboard/components/Dashboard'));
const DashboardOverview = React.lazy(() => import('@features/dashboard/components/DashboardOverview'));
const ProjectsList = React.lazy(() => import('@features/project/components/ProjectsList'));
const AdminCreation = React.lazy(() => import('@features/admin/components/AdminCreation'));
const AdminDetail = React.lazy(() => import('@features/admin/components/AdminDetail'));
const AdminApprovalNew = React.lazy(() => import('@features/admin/components/AdminApprovalNew'));
const PendingApprovals = React.lazy(() => import('@features/admin/components/PendingApprovals'));
const MenuManagement = React.lazy(() => import('@features/admin/components/MenuManagement'));

const UserList = React.lazy(() => import('@features/user/components/UserList'));
const UserDetail = React.lazy(() => import('@features/user/components/userdetail'));
const CompanyDetailsForm = React.lazy(() => import('@features/companydetails/companydetails'));
const ChatBox = React.lazy(() => import('@features/chatbox/components/chatbox'));
import RoleBasedRoute from './RoleBasedRoute';
// Removed unused manpower imports - files were cleaned up
const DailyAttendanceForm = React.lazy(() => import('@features/manpower/components/DailyAttendanceForm'));
const ConsolidatedManpowerView = React.lazy(() => import('@features/manpower/components/ConsolidatedManpowerView'));
const WorkerPage = React.lazy(() => import('@features/worker/pages/WorkerPage'));
const ToolboxTalkList = React.lazy(() => import('@features/toolboxtalk/components/ToolboxTalkList'));
const InductionTrainingList = React.lazy(() => import('@features/inductiontraining/components/InductionTrainingList'));
const JobTrainingList = React.lazy(() => import('@features/jobtraining').then(m => ({ default: m.JobTrainingList })));
const TrainingCheckInPage = React.lazy(() => import('@features/training/pages/TrainingCheckInPage'));
const IncidentManagementRoutes = React.lazy(() => import('@features/incidentmanagement/routes'));
const SafetyObservationFormPage = React.lazy(() => import('@features/safetyobservation/components/SafetyObservationFormPage'));
const SafetyObservationList = React.lazy(() => import('@features/safetyobservation/components/SafetyObservationList'));
const SafetyObservationEdit = React.lazy(() => import('@features/safetyobservation/components/SafetyObservationEdit'));
const SafetyObservationReview = React.lazy(() => import('@features/safetyobservation/components/SafetyObservationReview'));
const MomCreationForm = React.lazy(() => import('@features/mom/components/MomCreationForm'));
const MomList = React.lazy(() => import('@features/mom/components/MomList'));
const MomEdit = React.lazy(() => import('@features/mom/components/MomEdit'));
const MomView = React.lazy(() => import('@features/mom/components/MomView'));
const MomLive = React.lazy(() => import('@features/mom/components/MomLive'));
const MomWrapper = React.lazy(() => import('@features/mom/components/MomWrapper'));
const ParticipantResponse = React.lazy(() => import('@features/mom/components/ParticipantResponse'));
const TodoList = React.lazy(() => import('@common/components/todolist/TodoList'));
const PTWRoutes = React.lazy(() => import('../features/ptw/routes'));
const DocumentSignatureExample = React.lazy(() => import('@features/user/components/DocumentSignatureExample'));
const MobilePermitView = React.lazy(() => import('@features/ptw/components/MobilePermitView'));
const PermissionRequestsList = React.lazy(() => import('../components/permissions/PermissionRequestsList'));
const SystemSettings = React.lazy(() => import('@features/system').then(m => ({ default: m.SystemSettings })));
const SystemLogs = React.lazy(() => import('@features/system').then(m => ({ default: m.SystemLogs })));
const SystemBackup = React.lazy(() => import('@features/system').then(m => ({ default: m.SystemBackup })));
const InspectionList = React.lazy(() => import('@features/inspection/components/InspectionList'));
const InspectionCreate = React.lazy(() => import('@features/inspection/components/InspectionCreate'));
const InspectionReports = React.lazy(() => import('@features/inspection/components/InspectionReports'));
const ACCableInspectionForm = React.lazy(() => import('@features/inspection/components/forms/ACCableInspectionForm'));
const ACCableFormList = React.lazy(() => import('@features/inspection/components/forms/ACCableFormList'));
const ACDBChecklistForm = React.lazy(() => import('@features/inspection/components/forms/ACDBChecklistForm'));
const ACDBChecklistFormList = React.lazy(() => import('@features/inspection/components/forms/ACDBChecklistFormList'));
const HTCableChecklistForm = React.lazy(() => import('@features/inspection/components/forms/HTCableChecklistForm'));
const HTCableFormList = React.lazy(() => import('@features/inspection/components/forms/HTCableFormList'));
const HTPreCommissionForm = React.lazy(() => import('@features/inspection/components/forms/HTPreCommissionForm'));
const HTPreCommissionFormList = React.lazy(() => import('@features/inspection/components/forms/HTPreCommissionFormList'));
const HTPreCommissionTemplateForm = React.lazy(() => import('@features/inspection/components/forms/HTPreCommissionTemplateForm'));
const HTPreCommissionTemplateFormList = React.lazy(() => import('@features/inspection/components/forms/HTPreCommissionTemplateFormList'));
const CivilWorkChecklistForm = React.lazy(() => import('@features/inspection/components/forms/CivilWorkChecklistForm'));
const CivilWorkChecklistFormList = React.lazy(() => import('@features/inspection/components/forms/CivilWorkChecklistFormList'));
const CementRegisterForm = React.lazy(() => import('@features/inspection/components/forms/CementRegisterForm'));
const CementRegisterFormList = React.lazy(() => import('@features/inspection/components/forms/CementRegisterFormList'));
const ConcretePourCardForm = React.lazy(() => import('@features/inspection/components/forms/ConcretePourCardForm'));
const ConcretePourCardFormList = React.lazy(() => import('@features/inspection/components/forms/ConcretePourCardFormList'));
const PCCChecklistForm = React.lazy(() => import('@features/inspection/components/forms/PCCChecklistForm'));
const PCCChecklistFormList = React.lazy(() => import('@features/inspection/components/forms/PCCChecklistFormList'));
const BarBendingScheduleForm = React.lazy(() => import('@features/inspection/components/forms/BarBendingScheduleForm'));
const BarBendingScheduleFormList = React.lazy(() => import('@features/inspection/components/forms/BarBendingScheduleFormList'));
const BatteryChargerChecklistForm = React.lazy(() => import('@features/inspection/components/forms/BatteryChargerChecklistForm'));
const BatteryChargerChecklistFormList = React.lazy(() => import('@features/inspection/components/forms/BatteryChargerChecklistFormList'));
const BatteryUPSChecklistForm = React.lazy(() => import('@features/inspection/components/forms/BatteryUPSChecklistForm'));
const BatteryUPSChecklistFormList = React.lazy(() => import('@features/inspection/components/forms/BatteryUPSChecklistFormList'));
const BusDuctChecklistForm = React.lazy(() => import('@features/inspection/components/forms/BusDuctChecklistForm'));
const BusDuctChecklistFormList = React.lazy(() => import('@features/inspection/components/forms/BusDuctChecklistFormList'));
const ControlCableChecklistForm = React.lazy(() => import('@features/inspection/components/forms/ControlCableChecklistForm'));
const ControlCableChecklistFormList = React.lazy(() => import('@features/inspection/components/forms/ControlCableChecklistFormList'));
const ControlRoomAuditChecklistForm = React.lazy(() => import('@features/inspection/components/forms/ControlRoomAuditChecklistForm'));
const ControlRoomAuditChecklistFormList = React.lazy(() => import('@features/inspection/components/forms/ControlRoomAuditChecklistFormList'));
const EarthingChecklistForm = React.lazy(() => import('@features/inspection/components/forms/EarthingChecklistForm'));
const EarthingChecklistFormList = React.lazy(() => import('@features/inspection/components/forms/EarthingChecklistFormList'));

// ESG imports
const ESGOverview = React.lazy(() => import('@features/esg').then(m => ({ default: m.ESGOverview })));
const EnvironmentPage = React.lazy(() => import('@features/esg').then(m => ({ default: m.EnvironmentPage })));
const GovernancePage = React.lazy(() => import('@features/esg').then(m => ({ default: m.GovernancePage })));
const ESGReportsPage = React.lazy(() => import('@features/esg').then(m => ({ default: m.ESGReportsPage })));
const CarbonFootprintDashboard = React.lazy(() => import('@features/esg').then(m => ({ default: m.CarbonFootprintDashboard })));
const WaterManagementDashboard = React.lazy(() => import('@features/esg').then(m => ({ default: m.WaterManagementDashboard })));
const EnergyManagementDashboard = React.lazy(() => import('@features/esg').then(m => ({ default: m.EnergyManagementDashboard })));
const EnvironmentalIncidentDashboard = React.lazy(() => import('@features/esg').then(m => ({ default: m.EnvironmentalIncidentDashboard })));
const EnvironmentalMonitoringDashboard = React.lazy(() => import('@features/esg/components/EnvironmentalMonitoringDashboard'));
const SustainabilityTargetsDashboard = React.lazy(() => import('@features/esg/components/SustainabilityTargetsDashboard'));

// Quality Management imports
const QualityDashboard = React.lazy(() => import('@features/quality').then(m => ({ default: m.QualityDashboard })));
const QualityInspectionList = React.lazy(() => import('@features/quality').then(m => ({ default: m.QualityInspectionList })));
const InspectionForm = React.lazy(() => import('@features/quality').then(m => ({ default: m.InspectionForm })));
const SupplierQuality = React.lazy(() => import('@features/quality').then(m => ({ default: m.SupplierQuality })));
const DefectManagement = React.lazy(() => import('@features/quality').then(m => ({ default: m.DefectManagement })));
const QualityTemplates = React.lazy(() => import('@features/quality').then(m => ({ default: m.QualityTemplates })));
const QualityStandards = React.lazy(() => import('@features/quality').then(m => ({ default: m.QualityStandards })));
const QualityAlerts = React.lazy(() => import('@features/quality').then(m => ({ default: m.QualityAlerts })));
const QualityDashboardEnhanced = React.lazy(() => import('@features/quality/components/QualityDashboardEnhanced'));

// Alerts imports
const AlertsPage = React.lazy(() => import('@features/alerts/components/AlertsPage'));

// Analytics imports
const AnalyticsPage = React.lazy(() => import('@features/analytics/components/AnalyticsPage'));

// Notifications page
const NotificationsPage = React.lazy(() => import('../pages/Notifications'));

// PTW Redirect component for old test links
const PTWRedirect: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  return <Navigate to={`/dashboard/ptw/view/${id}`} replace />;
};

// ==================== FIX IS HERE (Step 1) ====================
// Import the new component to be used in the router.
const ProjectAttendance = React.lazy(() => import('@features/project/components/ProjectAttendance'));
// ===============================================================

// AI Bot Integration
const AIBotWidget = React.lazy(() => import('@features/ai_bot/components/AIBotWidget'));

// Voice Translator
const VoiceTranslator = React.lazy(() => import('../components/VoiceTranslator'));

import { useInductionTrainingEnforcement, InductionTrainingGuard } from '../hooks/useInductionTrainingEnforcement';

const SuperadminLayout = React.lazy(() => import('@features/superadmin/components/SuperadminLayout'));
const SuperadminDashboard = React.lazy(() => import('@features/superadmin/pages/SuperadminDashboard'));
const TenantsPage = React.lazy(() => import('@features/superadmin/pages/TenantsPage'));
const MastersPage = React.lazy(() => import('@features/superadmin/pages/MastersPage'));
const SubscriptionsPage = React.lazy(() => import('@features/superadmin/pages/SubscriptionsPage'));
const AuditLogsPage = React.lazy(() => import('@features/superadmin/pages/AuditLogsPage'));
const SuperadminSettings = React.lazy(() => import('@features/superadmin/pages/SuperadminSettings'));

// --- Helper components and event listeners ---
const ProfileWrapper: React.FC = () => {
  const { userToApprove, onApprovalSuccess } = useOutletContext<{
    userToApprove?: any | null;
    onApprovalSuccess?: (approvedUserId: number) => void;
  }>();
  return <UserDetail />;
};

window.addEventListener('error', (event) => {
  // Error logged to browser console automatically
  event.preventDefault();
  return true;
});

window.addEventListener('unhandledrejection', (event) => {
  // Error logged to browser console automatically
  event.preventDefault();
  return true;
});


// The main App component
// Protected Dashboard Component
const ProtectedDashboard: React.FC = () => {
  const { token, isAuthenticated, isSuperAdmin } = useAuthStore();

  // Check authentication before rendering Dashboard
  if (!token || !isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  if (isSuperAdmin) {
    return <Navigate to="/superadmin/dashboard" replace />;
  }

  return <Dashboard />;
};

const AppAliasRedirect: React.FC = () => {
  const location = useLocation();
  const target = location.pathname.replace('/app', '/dashboard') + location.search + location.hash;
  return <Navigate to={target} replace />;
};

const App: React.FC = () => {
  const token = useAuthStore((state) => state.token);
  const isPasswordResetRequired = useAuthStore((state) => state.isPasswordResetRequired);
  const isSuperAdmin = useAuthStore((state) => state.isSuperAdmin);
  const navigate = useNavigate();
  const location = useLocation();

  // CSRF token setup removed - not needed for current backend configuration

  useEffect(() => {
    // Prevent navigation loops during logout
    if (location.pathname === '/login') {
      return;
    }

    if (!token && location.pathname !== '/login') {
      navigate('/login', { replace: true });
    } else if (isPasswordResetRequired && location.pathname !== '/reset-password') {
      navigate('/reset-password', { replace: true });
    } else if (token && !isPasswordResetRequired && location.pathname === '/') {
      navigate(isSuperAdmin ? '/superadmin/dashboard' : '/dashboard', { replace: true });
    }
  }, [token, isPasswordResetRequired, isSuperAdmin, navigate, location.pathname]);
  
  const loadingSpinner = (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <Spin size="large" />
    </div>
  );

  return (
    <ErrorBoundary>
      <NotificationsProvider>
        <InductionTrainingGuard>
          <Suspense fallback={loadingSpinner}>
          <Routes>
            <Route path="/login" element={<SigninApp />} />
            <Route path="/superadmin" element={<SuperadminLayout />}>
              <Route index element={<Navigate to="dashboard" replace />} />
              <Route path="dashboard" element={<SuperadminDashboard />} />
              <Route path="tenants" element={<TenantsPage />} />
              <Route path="masters" element={<MastersPage />} />
              <Route path="subscriptions" element={<SubscriptionsPage />} />
              <Route path="audit-logs" element={<AuditLogsPage />} />
              <Route path="settings" element={<SuperadminSettings />} />
            </Route>
            <Route path="/app/*" element={<AppAliasRedirect />} />
            <Route path="/dashboard" element={<ProtectedDashboard />}>
              <Route index element={<DashboardOverview />} />
              
              {/* ==================== FIX IS HERE (Step 2) ==================== */}
              {/* Add a dedicated route for the attendance page so the URL works. */}
              <Route 
                path="attendance" 
                element={
                  <RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser', 'contractoruser', 'client', 'epc', 'contractor']}>
                    <ProjectAttendance />
                  </RoleBasedRoute>
                } 
              />
              {/* =============================================================== */}

              {/* --- All your other routes are unchanged --- */}
              <Route path="projects" element={<RoleBasedRoute allowedRoles={['masteradmin']}><ProjectsList /></RoleBasedRoute>} />
              <Route path="adminusers" element={<RoleBasedRoute allowedRoles={['masteradmin']}><AdminApprovalNew /></RoleBasedRoute>} />
              <Route path="admin-creation" element={<RoleBasedRoute allowedRoles={['masteradmin']}><AdminCreation /></RoleBasedRoute>} />
              <Route path="menu-management" element={<RoleBasedRoute allowedRoles={['masteradmin']}><MenuManagement /></RoleBasedRoute>} />

              {/* System Management Routes */}
              <Route path="system/settings" element={<RoleBasedRoute allowedRoles={['masteradmin']}><SystemSettings /></RoleBasedRoute>} />
              <Route path="system/logs" element={<RoleBasedRoute allowedRoles={['masteradmin']}><SystemLogs /></RoleBasedRoute>} />
              <Route path="system/backup" element={<RoleBasedRoute allowedRoles={['masteradmin']}><SystemBackup /></RoleBasedRoute>} />

              <Route path="admindetail" element={<RoleBasedRoute allowedRoles={['masteradmin', 'client', 'epc', 'contractor', 'contractor1', 'contractor2', 'contractor3', 'contractor4', 'contractor5', 'projectadmin']}><AdminDetail /></RoleBasedRoute>} />
              <Route path="pending-approvals" element={<RoleBasedRoute allowedRoles={['masteradmin']}><PendingApprovals /></RoleBasedRoute>} />
              <Route path="users" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor', 'contractor1', 'contractor2', 'contractor3', 'contractor4', 'contractor5']}><UserList /></RoleBasedRoute>} />
              <Route path="userdetail" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser', 'contractoruser']}><UserDetail /></RoleBasedRoute>} />
              <Route path="profile" element={<ProfileWrapper />} />
              <Route path="settings" element={<CompanyDetailsForm />} />
              <Route path="chatbox" element={<RoleBasedRoute allowedRoles={['clientuser', 'contractoruser', 'epcuser']}><ChatBox /></RoleBasedRoute>} />
              <Route path="ai-bot" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser', 'contractoruser']}><AIBotWidget /></RoleBasedRoute>} />
              <Route path="voice-translator" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser', 'contractoruser']}><VoiceTranslator /></RoleBasedRoute>} />
              {/* Main manpower page shows list with CRUD operations */}
              <Route path="manpower" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ConsolidatedManpowerView /></RoleBasedRoute>} />
              <Route path="manpower/add" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><DailyAttendanceForm /></RoleBasedRoute>} />
              <Route path="manpower/reports" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ConsolidatedManpowerView /></RoleBasedRoute>} />
              {/* Removed legacy manpower routes - components were cleaned up */}
              <Route path="workers" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor', 'contractor1', 'contractor2', 'contractor3', 'contractor4', 'contractor5', 'clientuser', 'epcuser', 'contractoruser']}><WorkerPage /></RoleBasedRoute>} />
              <Route path="toolboxtalk" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser', 'contractoruser']}><ToolboxTalkList /></RoleBasedRoute>} />
              <Route path="inductiontraining" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor', 'contractor1', 'contractor2', 'contractor3', 'contractor4', 'contractor5', 'clientuser', 'epcuser', 'contractoruser', 'adminuser']}><InductionTrainingList /></RoleBasedRoute>} />
              <Route path="jobtraining" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><JobTrainingList /></RoleBasedRoute>} />
              <Route
                path="training/check-in"
                element={
                  <RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser', 'contractoruser', 'client', 'epc', 'contractor', 'masteradmin', 'projectadmin']}>
                    <TrainingCheckInPage />
                  </RoleBasedRoute>
                }
              />
              <Route path="mom" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser']}><MomWrapper /></RoleBasedRoute>}>
                <Route index element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser']}><MomList /></RoleBasedRoute>} />
                <Route path="schedule" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser']}><MomCreationForm /></RoleBasedRoute>} />
                <Route path="edit/:id" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser']}><MomEdit /></RoleBasedRoute>} />
                <Route path="view/:id" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser']}><MomView /></RoleBasedRoute>} />
<Route path="live/:id" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser']}><MomLive /></RoleBasedRoute>} />
              </Route>
              <Route path="incidentmanagement/*" element={<IncidentManagementRoutes />} />
              {/* Safety Observation Routes - Review route MUST come before edit route to avoid conflicts */}
              <Route path="safetyobservation/review/:observationID" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser', 'contractoruser', 'client', 'epc', 'contractor']}><SafetyObservationReview /></RoleBasedRoute>} />
              <Route path="safetyobservation/form" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser', 'contractoruser', 'client', 'epc', 'contractor']}><SafetyObservationFormPage /></RoleBasedRoute>} />
              <Route path="safetyobservation/list" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser', 'contractoruser', 'client', 'epc', 'contractor']}><SafetyObservationList /></RoleBasedRoute>} />
              <Route path="safetyobservation/edit/:observationID" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser', 'contractoruser', 'client', 'epc', 'contractor']}><SafetyObservationEdit /></RoleBasedRoute>} />


              <Route path="todolist" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser']}><TodoList /></RoleBasedRoute>} />
              <Route path="permissions/requests" element={<RoleBasedRoute allowedRoles={['masteradmin', 'client', 'epc', 'contractor']}><PermissionRequestsList /></RoleBasedRoute>} />
              <Route path="signature-demo" element={<RoleBasedRoute allowedRoles={['adminuser', 'clientuser', 'epcuser', 'contractoruser']}><DocumentSignatureExample /></RoleBasedRoute>} />

              {/* Redirect old PTW test links to correct routes */}
              <Route path="ptw-test/:id" element={<PTWRedirect />} />

              <Route path="ptw/*" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser', 'masteradmin', 'adminuser']}><PTWRoutes /></RoleBasedRoute>} />
              
              {/* Inspection Routes */}
              <Route path="inspection/reports" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><InspectionReports /></RoleBasedRoute>} />
              <Route path="inspection/create" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><InspectionCreate /></RoleBasedRoute>} />
              <Route path="inspection" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><InspectionList /></RoleBasedRoute>} />
              <Route path="inspection/forms/ac-cable-testing" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ACCableFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/ac-cable-testing/list" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ACCableFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/ac-cable-testing/create" element={<RoleBasedRoute allowedRoles={['epcuser']}><ACCableInspectionForm /></RoleBasedRoute>} />
              <Route path="inspection/forms/acdb-checklist" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ACDBChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/acdb-checklist/list" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ACDBChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/acdb-checklist/create" element={<RoleBasedRoute allowedRoles={['epcuser']}><ACDBChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/forms/ht-cable" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><HTCableFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/ht-cable/list" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><HTCableFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/ht-cable/create" element={<RoleBasedRoute allowedRoles={['epcuser']}><HTCableChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/forms/ht-precommission" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><HTPreCommissionFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/ht-precommission/list" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><HTPreCommissionFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/ht-precommission/create" element={<RoleBasedRoute allowedRoles={['epcuser']}><HTPreCommissionForm /></RoleBasedRoute>} />
              <Route path="inspection/forms/ht-precommission-template" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><HTPreCommissionTemplateFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/ht-precommission-template/list" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><HTPreCommissionTemplateFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/ht-precommission-template/create" element={<RoleBasedRoute allowedRoles={['epcuser']}><HTPreCommissionTemplateForm /></RoleBasedRoute>} />
              <Route path="inspection/forms/civil-work-checklist" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><CivilWorkChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/civil-work-checklist/list" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><CivilWorkChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/civil-work-checklist/create" element={<RoleBasedRoute allowedRoles={['epcuser']}><CivilWorkChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/cement-register-forms" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><CementRegisterFormList /></RoleBasedRoute>} />
              <Route path="inspection/cement-register-forms/new" element={<RoleBasedRoute allowedRoles={['epcuser']}><CementRegisterForm /></RoleBasedRoute>} />
              <Route path="inspection/cement-register-forms/:id" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><CementRegisterForm /></RoleBasedRoute>} />
              <Route path="inspection/cement-register-forms/:id/edit" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor']}><CementRegisterForm /></RoleBasedRoute>} />
              <Route path="inspection/concrete-pour-card-forms" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ConcretePourCardFormList /></RoleBasedRoute>} />
              <Route path="inspection/concrete-pour-card-forms/new" element={<RoleBasedRoute allowedRoles={['epcuser']}><ConcretePourCardForm /></RoleBasedRoute>} />
              <Route path="inspection/concrete-pour-card-forms/:id" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ConcretePourCardForm /></RoleBasedRoute>} />
              <Route path="inspection/concrete-pour-card-forms/:id/edit" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor']}><ConcretePourCardForm /></RoleBasedRoute>} />
              <Route path="inspection/pcc-checklist-forms" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><PCCChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/pcc-checklist-forms/new" element={<RoleBasedRoute allowedRoles={['epcuser']}><PCCChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/pcc-checklist-forms/:id" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><PCCChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/pcc-checklist-forms/:id/edit" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor']}><PCCChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/bar-bending-schedule-forms" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><BarBendingScheduleFormList /></RoleBasedRoute>} />
              <Route path="inspection/bar-bending-schedule-forms/new" element={<RoleBasedRoute allowedRoles={['epcuser']}><BarBendingScheduleForm /></RoleBasedRoute>} />
              <Route path="inspection/bar-bending-schedule-forms/:id" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><BarBendingScheduleForm /></RoleBasedRoute>} />
              <Route path="inspection/bar-bending-schedule-forms/:id/edit" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor']}><BarBendingScheduleForm /></RoleBasedRoute>} />
              <Route path="inspection/battery-charger-checklist-forms" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><BatteryChargerChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/battery-charger-checklist-forms/new" element={<RoleBasedRoute allowedRoles={['epcuser']}><BatteryChargerChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/battery-charger-checklist-forms/:id" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><BatteryChargerChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/battery-charger-checklist-forms/:id/edit" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor']}><BatteryChargerChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/battery-ups-checklist-forms" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><BatteryUPSChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/battery-ups-checklist-forms/new" element={<RoleBasedRoute allowedRoles={['epcuser']}><BatteryUPSChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/battery-ups-checklist-forms/:id" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><BatteryUPSChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/battery-ups-checklist-forms/:id/edit" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor']}><BatteryUPSChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/bus-duct-checklist-forms" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><BusDuctChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/bus-duct-checklist-forms/new" element={<RoleBasedRoute allowedRoles={['epcuser']}><BusDuctChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/bus-duct-checklist-forms/:id" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><BusDuctChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/bus-duct-checklist-forms/:id/edit" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor']}><BusDuctChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/control-cable-checklist-forms" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ControlCableChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/control-cable-checklist-forms/new" element={<RoleBasedRoute allowedRoles={['epcuser']}><ControlCableChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/control-cable-checklist-forms/:id" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ControlCableChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/control-cable-checklist-forms/:id/edit" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor']}><ControlCableChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/control-room-audit-checklist" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ControlRoomAuditChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/control-room-audit-checklist/new" element={<RoleBasedRoute allowedRoles={['epcuser']}><ControlRoomAuditChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/control-room-audit-checklist/view/:id" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><ControlRoomAuditChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/control-room-audit-checklist/edit/:id" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor']}><ControlRoomAuditChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/forms/earthing-checklist" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><EarthingChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/earthing-checklist/list" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><EarthingChecklistFormList /></RoleBasedRoute>} />
              <Route path="inspection/forms/earthing-checklist/create" element={<RoleBasedRoute allowedRoles={['epcuser']}><EarthingChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/forms/earthing-checklist/:id" element={<RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'adminuser']}><EarthingChecklistForm /></RoleBasedRoute>} />
              <Route path="inspection/forms/earthing-checklist/:id/edit" element={<RoleBasedRoute allowedRoles={['client', 'epc', 'contractor']}><EarthingChecklistForm /></RoleBasedRoute>} />
              
              {/* ESG Routes */}
              <Route path="esg" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><ESGOverview /></RoleBasedRoute>} />
              <Route path="esg/environment" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><EnvironmentPage /></RoleBasedRoute>} />
              <Route path="esg/monitoring" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><EnvironmentalMonitoringDashboard /></RoleBasedRoute>} />
              <Route path="esg/carbon-footprint" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><CarbonFootprintDashboard /></RoleBasedRoute>} />
              <Route path="esg/water-management" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><WaterManagementDashboard /></RoleBasedRoute>} />
              <Route path="esg/energy-management" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><EnergyManagementDashboard /></RoleBasedRoute>} />
              <Route path="esg/environmental-incidents" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><EnvironmentalIncidentDashboard /></RoleBasedRoute>} />
              <Route path="esg/sustainability-targets" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><SustainabilityTargetsDashboard /></RoleBasedRoute>} />
              <Route path="esg/governance" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><GovernancePage /></RoleBasedRoute>} />
              <Route path="esg/reports" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><ESGReportsPage /></RoleBasedRoute>} />
              
              {/* Quality Management Routes */}
              <Route path="quality" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><QualityDashboard /></RoleBasedRoute>} />
              <Route path="quality/enhanced" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><QualityDashboardEnhanced /></RoleBasedRoute>} />
              <Route path="quality/inspections" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><QualityInspectionList /></RoleBasedRoute>} />
              <Route path="quality/inspections/create" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><InspectionForm mode="create" /></RoleBasedRoute>} />
              <Route path="quality/suppliers" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><SupplierQuality /></RoleBasedRoute>} />
              <Route path="quality/defects" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><DefectManagement /></RoleBasedRoute>} />
              <Route path="quality/templates" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><QualityTemplates /></RoleBasedRoute>} />
              <Route path="quality/standards" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><QualityStandards /></RoleBasedRoute>} />
              <Route path="quality/alerts" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><QualityAlerts /></RoleBasedRoute>} />
              
              {/* General Alerts Route - Master Admin excluded */}
              <Route path="alerts" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><AlertsPage /></RoleBasedRoute>} />
              
              {/* Analytics Route */}
              <Route path="analytics" element={<RoleBasedRoute allowedRoles={['adminuser', 'client', 'epc', 'contractor', 'clientuser', 'epcuser', 'contractoruser']}><AnalyticsPage /></RoleBasedRoute>} />
              
              {/* Notifications Route */}
              <Route path="notifications" element={<NotificationsPage />} />
            </Route>
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="participant-response/:momId/:userId" element={<ParticipantResponse />} />
            <Route path="mobile/permit/:permitId" element={<MobilePermitView />} />
            <Route path="*" element={<SigninApp />} />
          </Routes>
        </Suspense>
        </InductionTrainingGuard>
      </NotificationsProvider>
    </ErrorBoundary>
  );
};

export default App;
