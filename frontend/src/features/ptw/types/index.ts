// Define the PermitType interface
export interface PermitType {
  id: number;
  name: string;
  description?: string;
  color_code?: string;
  risk_level?: 'low' | 'medium' | 'high' | 'critical';
  validity_hours?: number;
  requires_approval_levels?: number;
  active?: boolean;
}

// Permit interface - authorization is handled by workflow system
export interface Permit {
  id: number;
  permit_number: string;
  title: string;
  permit_type: number;
  permit_type_details?: PermitType;
  location: string;
  description: string;
  planned_start_time: string;
  planned_end_time: string;
  actual_start_time?: string;
  actual_end_time?: string;
  created_by: number;
  created_by_details?: UserMinimal;
  status: PermitStatus;
  current_approval_level?: number;
  created_at: string;
  updated_at: string;
  hazards?: string;
  control_measures?: string;
  ppe_requirements?: string;
  special_instructions?: string;
  // Workflow-managed fields (read-only)
  verifier?: number;
  verifier_details?: UserMinimal;
  verified_at?: string;
  verification_comments?: string;
  approved_by?: number;
  approved_by_details?: UserMinimal;
  approved_at?: string;
  approval_comments?: string;
}

// Update the PermitStatus type to include verification statuses
export type PermitStatus = 
  | 'draft'
  | 'pending_verification'
  | 'verified'
  | 'pending_approval'
  | 'approved'
  | 'rejected'
  | 'in_progress'
  | 'completed'
  | 'closed'
  | 'suspended'
  | 'cancelled';

// Update the UserMinimal interface to include admin_type and grade properties
export interface UserMinimal {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  name?: string;
  usertype?: string; // Changed from admin_type to usertype
  grade?: string;
}









