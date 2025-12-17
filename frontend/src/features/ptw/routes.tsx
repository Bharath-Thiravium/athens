import React from 'react';
import { Routes, Route } from 'react-router-dom';
import RoleBasedRoute from '../../app/RoleBasedRoute';
import PermitList from './components/PermitList';
import EnhancedPermitForm from './components/EnhancedPermitForm';
import PermitDetail from './components/PermitDetail';
import ComplianceDashboard from './components/ComplianceDashboard';
import WorkflowTaskDashboard from './components/WorkflowTaskDashboard';
import PTWLayout from './components/PTWLayout';

const PTWRoutes: React.FC = () => {
  return (
    <Routes>
      <Route element={<PTWLayout />}>
        <Route 
          index 
          element={
            <RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'client','epc','contractor']}>
              <PermitList />
            </RoleBasedRoute>
          } 
        />
        <Route 
          path="create" 
          element={
            <RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'epc','client','contractor']}>
              <EnhancedPermitForm />
            </RoleBasedRoute>
          } 
        />
        <Route 
          path="edit/:id" 
          element={
            <RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'client','epc','contractor']}>
              <EnhancedPermitForm />
            </RoleBasedRoute>
          } 
        />
        <Route 
          path="view/:id" 
          element={
            <RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'client','epc','contractor']}>
              <PermitDetail />
            </RoleBasedRoute>
          } 
        />
        <Route 
          path="dashboard" 
          element={
            <RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'client','epc','contractor']}>
              <ComplianceDashboard />
            </RoleBasedRoute>
          } 
        />
        <Route 
          path="pending-approvals" 
          element={
            <RoleBasedRoute allowedRoles={['clientuser', 'epcuser', 'contractoruser', 'client','epc','contractor']}>
              <WorkflowTaskDashboard />
            </RoleBasedRoute>
          } 
        />
      </Route>
    </Routes>
  );
};

export default PTWRoutes;




