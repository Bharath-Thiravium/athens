/**
 * Centralized Form Validation Utility
 * Fixes validation logic issues across all forms
 */

import { Rule } from 'antd/es/form';
import dayjs from 'dayjs';

export const ValidationRules = {
  // Required field validation
  required: (message?: string): Rule => ({
    required: true,
    message: message || 'This field is required',
    whitespace: true
  }),

  // Email validation with proper regex
  email: (): Rule => ({
    type: 'email',
    message: 'Please enter a valid email address',
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  }),

  // Username validation - alphanumeric, underscore, dot, hyphen
  username: (): Rule[] => [
    ValidationRules.required('Username is required'),
    {
      min: 3,
      max: 150,
      message: 'Username must be between 3 and 150 characters'
    },
    {
      pattern: /^[a-zA-Z0-9._@-]+$/,
      message: 'Username can only contain letters, numbers, dots, underscores, @ and hyphens'
    }
  ],

  // Password validation
  password: (minLength: number = 8): Rule[] => [
    ValidationRules.required('Password is required'),
    {
      min: minLength,
      max: 128,
      message: `Password must be between ${minLength} and 128 characters`
    }
  ],

  // Text length validation
  textLength: (min: number = 0, max: number = 255, fieldName: string = 'Field'): Rule[] => {
    const rules: Rule[] = [];
    
    if (min > 0) {
      rules.push({
        min,
        message: `${fieldName} must be at least ${min} characters`
      });
    }
    
    rules.push({
      max,
      message: `${fieldName} cannot exceed ${max} characters`
    });
    
    return rules;
  },

  // Number validation
  number: (min?: number, max?: number, message?: string): Rule => ({
    type: 'number',
    min,
    max,
    message: message || `Please enter a valid number${min !== undefined ? ` (min: ${min})` : ''}${max !== undefined ? ` (max: ${max})` : ''}`
  }),

  // Date validation - no future dates
  pastDate: (message?: string): Rule => ({
    validator: (_, value) => {
      if (!value) return Promise.resolve();
      if (dayjs(value).isAfter(dayjs())) {
        return Promise.reject(new Error(message || 'Date cannot be in the future'));
      }
      return Promise.resolve();
    }
  }),

  // Phone number validation
  phone: (): Rule => ({
    pattern: /^[\+]?[1-9][\d]{0,15}$/,
    message: 'Please enter a valid phone number'
  }),

  // URL validation
  url: (): Rule => ({
    type: 'url',
    message: 'Please enter a valid URL'
  }),

  // File size validation (in MB)
  fileSize: (maxSizeMB: number = 5): Rule => ({
    validator: (_, fileList) => {
      if (!fileList || fileList.length === 0) return Promise.resolve();
      
      const oversizedFiles = fileList.filter((file: any) => {
        const size = file.size || file.originFileObj?.size || 0;
        return size > maxSizeMB * 1024 * 1024;
      });
      
      if (oversizedFiles.length > 0) {
        return Promise.reject(new Error(`File size must be less than ${maxSizeMB}MB`));
      }
      
      return Promise.resolve();
    }
  }),

  // File type validation
  fileType: (allowedTypes: string[]): Rule => ({
    validator: (_, fileList) => {
      if (!fileList || fileList.length === 0) return Promise.resolve();
      
      const invalidFiles = fileList.filter((file: any) => {
        const type = file.type || file.originFileObj?.type || '';
        return !allowedTypes.includes(type);
      });
      
      if (invalidFiles.length > 0) {
        return Promise.reject(new Error(`Only ${allowedTypes.join(', ')} files are allowed`));
      }
      
      return Promise.resolve();
    }
  }),

  // Permit type validation
  permitType: (): Rule[] => [
    ValidationRules.required('Please select a permit type'),
    {
      validator: (_, value) => {
        if (!value || (Array.isArray(value) && value.length === 0)) {
          return Promise.reject(new Error('Please select a permit type'));
        }
        
        // Handle array values (fix for permit type selection issue)
        const actualValue = Array.isArray(value) ? value[0] : value;
        
        if (!actualValue || isNaN(Number(actualValue))) {
          return Promise.reject(new Error('Invalid permit type selected'));
        }
        
        return Promise.resolve();
      }
    }
  ],

  // Risk assessment validation
  riskScore: (min: number = 1, max: number = 5): Rule[] => [
    ValidationRules.required('Please select a risk score'),
    ValidationRules.number(min, max, `Risk score must be between ${min} and ${max}`)
  ],

  // Location validation with GPS coordinates
  location: (): Rule[] => [
    ValidationRules.required('Location is required'),
    ...ValidationRules.textLength(3, 255, 'Location')
  ],

  // GPS coordinates validation
  gpsCoordinates: (): Rule => ({
    pattern: /^-?([1-8]?[1-9]|[1-9]0)\.{1}\d{1,6},-?([1-8]?[1-9]|[1-9]0)\.{1}\d{1,6}$/,
    message: 'Please enter valid GPS coordinates (lat,lng format)'
  }),

  // Work description validation
  workDescription: (): Rule[] => [
    ValidationRules.required('Work description is required'),
    ...ValidationRules.textLength(10, 1000, 'Work description')
  ],

  // Safety checklist validation
  safetyChecklist: (minItems: number = 1): Rule => ({
    validator: (_, value) => {
      if (!value || (Array.isArray(value) && value.length < minItems)) {
        return Promise.reject(new Error(`Please check at least ${minItems} safety item(s)`));
      }
      return Promise.resolve();
    }
  }),

  // PPE requirements validation
  ppeRequirements: (): Rule => ({
    validator: (_, value) => {
      if (!value || (Array.isArray(value) && value.length === 0)) {
        return Promise.reject(new Error('Please select required PPE'));
      }
      return Promise.resolve();
    }
  }),

  // Incident severity validation
  incidentSeverity: (): Rule[] => [
    ValidationRules.required('Please select incident severity'),
    {
      validator: (_, value) => {
        const validSeverities = ['low', 'medium', 'high', 'critical'];
        if (!validSeverities.includes(value)) {
          return Promise.reject(new Error('Invalid severity level'));
        }
        return Promise.resolve();
      }
    }
  ]
};

// Form validation helpers
export const FormValidationHelpers = {
  // Validate form step
  validateFormStep: async (form: any, fields: string[]): Promise<boolean> => {
    try {
      await form.validateFields(fields);
      return true;
    } catch (error) {
      return false;
    }
  },

  // Get validation errors
  getValidationErrors: (errorInfo: any): string[] => {
    if (!errorInfo?.errorFields) return [];
    
    return errorInfo.errorFields.map((field: any) => 
      field.errors?.[0] || 'Validation error'
    );
  },

  // Clean form data before submission
  cleanFormData: (data: any): any => {
    const cleaned = { ...data };
    
    // Handle permit type arrays
    if (Array.isArray(cleaned.permit_type)) {
      cleaned.permit_type = cleaned.permit_type[0];
    }
    
    // Convert string numbers to actual numbers
    ['probability', 'severity', 'permit_type'].forEach(field => {
      if (cleaned[field] && typeof cleaned[field] === 'string') {
        const num = Number(cleaned[field]);
        if (!isNaN(num)) {
          cleaned[field] = num;
        }
      }
    });
    
    // Trim string fields
    Object.keys(cleaned).forEach(key => {
      if (typeof cleaned[key] === 'string') {
        cleaned[key] = cleaned[key].trim();
      }
    });
    
    // Convert dayjs dates to ISO strings
    Object.keys(cleaned).forEach(key => {
      if (cleaned[key] && typeof cleaned[key] === 'object' && cleaned[key].toISOString) {
        cleaned[key] = cleaned[key].toISOString();
      }
    });
    
    return cleaned;
  },

  // Validate file uploads
  validateFileUpload: (file: any, maxSizeMB: number = 5, allowedTypes: string[] = []): boolean => {
    // Check file size
    if (file.size > maxSizeMB * 1024 * 1024) {
      return false;
    }
    
    // Check file type if specified
    if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
      return false;
    }
    
    return true;
  },

  // Sanitize input to prevent XSS
  sanitizeInput: (input: string): string => {
    if (typeof input !== 'string') return input;
    
    return input
      .replace(/[<>]/g, '') // Remove < and >
      .replace(/javascript:/gi, '') // Remove javascript: protocol
      .replace(/on\w+=/gi, '') // Remove event handlers
      .trim();
  }
};

export default ValidationRules;