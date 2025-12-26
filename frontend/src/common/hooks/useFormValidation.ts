/**
 * Custom hook for form validation
 * Provides standardized validation logic across all forms
 */

import { useState, useCallback } from 'react';
import { Form, message } from 'antd';
import { ValidationRules, FormValidationHelpers } from '../utils/formValidation';

interface UseFormValidationOptions {
  onSuccess?: (data: any) => void | Promise<void>;
  onError?: (error: any) => void;
  validateOnChange?: boolean;
  showSuccessMessage?: boolean;
  successMessage?: string;
}

export const useFormValidation = (options: UseFormValidationOptions = {}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string[]>>({});

  const {
    onSuccess,
    onError,
    validateOnChange = false,
    showSuccessMessage = true,
    successMessage = 'Form submitted successfully'
  } = options;

  // Validate specific fields
  const validateFields = useCallback(async (fields?: string[]): Promise<boolean> => {
    try {
      await form.validateFields(fields);
      setErrors({});
      return true;
    } catch (errorInfo) {
      const validationErrors = FormValidationHelpers.getValidationErrors(errorInfo);
      const errorMap: Record<string, string[]> = {};
      
      errorInfo.errorFields?.forEach((field: any) => {
        errorMap[field.name[0]] = field.errors;
      });
      
      setErrors(errorMap);
      return false;
    }
  }, [form]);

  // Submit form with validation
  const submitForm = useCallback(async (customData?: any) => {
    setLoading(true);
    try {
      // Validate all fields first
      const isValid = await validateFields();
      if (!isValid) {
        message.error('Please fix validation errors before submitting');
        return false;
      }

      // Get form values
      const formValues = customData || form.getFieldsValue();
      
      // Clean form data
      const cleanedData = FormValidationHelpers.cleanFormData(formValues);

      // Call success handler
      if (onSuccess) {
        await onSuccess(cleanedData);
      }

      // Show success message
      if (showSuccessMessage) {
        message.success(successMessage);
      }

      setErrors({});
      return true;
    } catch (error: any) {
      console.error('Form submission error:', error);
      
      // Handle API validation errors
      if (error?.response?.data && typeof error.response.data === 'object') {
        const apiErrors: Record<string, string[]> = {};
        
        Object.keys(error.response.data).forEach(field => {
          const fieldError = error.response.data[field];
          apiErrors[field] = Array.isArray(fieldError) ? fieldError : [fieldError];
        });
        
        setErrors(apiErrors);
        form.setFields(Object.keys(apiErrors).map(field => ({
          name: field,
          errors: apiErrors[field]
        })));
      }

      // Call error handler
      if (onError) {
        onError(error);
      } else {
        message.error(error?.message || 'Form submission failed');
      }

      return false;
    } finally {
      setLoading(false);
    }
  }, [form, onSuccess, onError, showSuccessMessage, successMessage, validateFields]);

  // Reset form and errors
  const resetForm = useCallback(() => {
    form.resetFields();
    setErrors({});
  }, [form]);

  // Set field error
  const setFieldError = useCallback((field: string, error: string) => {
    setErrors(prev => ({
      ...prev,
      [field]: [error]
    }));
    
    form.setFields([{
      name: field,
      errors: [error]
    }]);
  }, [form]);

  // Clear field error
  const clearFieldError = useCallback((field: string) => {
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[field];
      return newErrors;
    });
    
    form.setFields([{
      name: field,
      errors: []
    }]);
  }, [form]);

  // Handle form value changes
  const handleValuesChange = useCallback((changedValues: any, allValues: any) => {
    if (validateOnChange) {
      // Validate changed fields
      Object.keys(changedValues).forEach(field => {
        form.validateFields([field]).catch(() => {
          // Validation error will be handled by form
        });
      });
    }
  }, [form, validateOnChange]);

  return {
    form,
    loading,
    errors,
    validateFields,
    submitForm,
    resetForm,
    setFieldError,
    clearFieldError,
    handleValuesChange,
    
    // Validation rules for easy access
    rules: ValidationRules,
    
    // Form props for easy spreading
    formProps: {
      form,
      onValuesChange: handleValuesChange,
      onFinish: submitForm,
      onFinishFailed: (errorInfo: any) => {
        const validationErrors = FormValidationHelpers.getValidationErrors(errorInfo);
        message.error(validationErrors[0] || 'Please fix validation errors');
      }
    }
  };
};

export default useFormValidation;