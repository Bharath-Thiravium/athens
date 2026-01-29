/**
 * Enhanced Error Handling Utility
 * Provides comprehensive error handling with specific error types and user-friendly messages
 */

import { message } from 'antd';
import { safeLog } from './logSanitizer';

export interface ApiError {
  status?: number;
  statusText?: string;
  data?: any;
  message?: string;
  code?: string;
}

export interface ErrorContext {
  component?: string;
  action?: string;
  userId?: number;
  additionalInfo?: Record<string, any>;
}

export class AppError extends Error {
  public status?: number;
  public code?: string;
  public context?: ErrorContext;

  constructor(message: string, status?: number, code?: string, context?: ErrorContext) {
    super(message);
    this.name = 'AppError';
    this.status = status;
    this.code = code;
    this.context = context;
  }
}

export const ErrorTypes = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NOT_FOUND_ERROR: 'NOT_FOUND_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR'
} as const;

export const normalizeErrorMessage = (value: any, fallback = ''): string => {
  if (value === null || value === undefined) {
    return fallback;
  }
  if (typeof value === 'string') {
    return value;
  }
  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }
  if (Array.isArray(value)) {
    const parts = value
      .map((item) => normalizeErrorMessage(item, ''))
      .filter(Boolean);
    return parts.length ? parts.join(', ') : fallback;
  }
  if (typeof value === 'object') {
    const candidate =
      (value as any).message ??
      (value as any).detail ??
      (value as any).error ??
      (value as any).code;
    if (candidate !== undefined) {
      return normalizeErrorMessage(candidate, fallback);
    }
    try {
      return JSON.stringify(value);
    } catch (err) {
      return fallback;
    }
  }
  return String(value);
};

export const getErrorType = (error: any): string => {
  if (!error.response) {
    return ErrorTypes.NETWORK_ERROR;
  }

  const status = error.response.status;
  
  switch (status) {
    case 401:
      return ErrorTypes.AUTHENTICATION_ERROR;
    case 403:
      return ErrorTypes.AUTHORIZATION_ERROR;
    case 404:
      return ErrorTypes.NOT_FOUND_ERROR;
    case 422:
    case 400:
      return ErrorTypes.VALIDATION_ERROR;
    case 500:
    case 502:
    case 503:
      return ErrorTypes.SERVER_ERROR;
    default:
      return ErrorTypes.UNKNOWN_ERROR;
  }
};

export const getErrorMessage = (error: any, context?: ErrorContext): string => {
  const errorType = getErrorType(error);
  const defaultMessages = {
    [ErrorTypes.NETWORK_ERROR]: 'Network connection failed. Please check your internet connection and try again.',
    [ErrorTypes.AUTHENTICATION_ERROR]: 'Authentication failed. Please log in again.',
    [ErrorTypes.AUTHORIZATION_ERROR]: 'You do not have permission to perform this action.',
    [ErrorTypes.VALIDATION_ERROR]: 'Please check your input and try again.',
    [ErrorTypes.NOT_FOUND_ERROR]: 'The requested resource was not found.',
    [ErrorTypes.SERVER_ERROR]: 'Server error occurred. Please try again later.',
    [ErrorTypes.UNKNOWN_ERROR]: 'An unexpected error occurred. Please try again.'
  };

  // Try to get specific error message from response
  if (error.response?.data?.message) {
    return normalizeErrorMessage(error.response.data.message, defaultMessages[errorType as keyof typeof defaultMessages]);
  }

  if (error.response?.data?.error) {
    return normalizeErrorMessage(error.response.data.error, defaultMessages[errorType as keyof typeof defaultMessages]);
  }

  if (error.message) {
    return normalizeErrorMessage(error.message, defaultMessages[errorType as keyof typeof defaultMessages]);
  }

  return defaultMessages[errorType as keyof typeof defaultMessages];
};

export const handleApiError = (error: any, context?: ErrorContext): AppError => {
  const errorType = getErrorType(error);
  const errorMessage = getErrorMessage(error, context);
  const status = error.response?.status;
  
  // Log the error securely
  safeLog.error('API Error occurred', {
    type: errorType,
    status,
    message: errorMessage,
    context,
    url: error.config?.url,
    method: error.config?.method
  });

  // Show user-friendly message
  switch (errorType) {
    case ErrorTypes.NETWORK_ERROR:
      message.error('Connection failed. Please check your internet connection.');
      break;
    case ErrorTypes.AUTHENTICATION_ERROR:
      message.error('Please log in again to continue.');
      break;
    case ErrorTypes.AUTHORIZATION_ERROR:
      message.error('You do not have permission for this action.');
      break;
    case ErrorTypes.VALIDATION_ERROR:
      message.error(errorMessage);
      break;
    case ErrorTypes.NOT_FOUND_ERROR:
      message.error('Resource not found.');
      break;
    case ErrorTypes.SERVER_ERROR:
      message.error('Server error. Please try again later.');
      break;
    default:
      message.error('An unexpected error occurred.');
  }

  return new AppError(errorMessage, status, errorType, context);
};

export const handleAsyncError = async <T>(
  asyncFn: () => Promise<T>,
  context?: ErrorContext
): Promise<T | null> => {
  try {
    return await asyncFn();
  } catch (error: unknown) {
    handleApiError(error, context);
    return null;
  }
};

export const withErrorBoundary = <T extends any[], R>(
  fn: (...args: T) => R,
  context?: ErrorContext
) => {
  return (...args: T): R | null => {
    try {
      return fn(...args);
    } catch (error) {
      handleApiError(error, context);
      return null;
    }
  };
};

// Retry mechanism for failed requests
export const retryRequest = async <T>(
  requestFn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000,
  context?: ErrorContext
): Promise<T | null> => {
  let lastError: any;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      
      if (attempt === maxRetries) {
        break;
      }

      // Don't retry on authentication or authorization errors
      const errorType = getErrorType(error);
      if (errorType === ErrorTypes.AUTHENTICATION_ERROR || 
          errorType === ErrorTypes.AUTHORIZATION_ERROR) {
        break;
      }

      safeLog.warn(`Request attempt ${attempt} failed, retrying in ${delay}ms`, {
        context,
        error: error.message
      });

      await new Promise(resolve => setTimeout(resolve, delay));
      delay *= 2; // Exponential backoff
    }
  }

  return handleAsyncError(() => Promise.reject(lastError), context);
};
