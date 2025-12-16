/**
 * Log Sanitizer Utility
 * Prevents log injection attacks by sanitizing user input before logging
 */

export const sanitizeForLog = (input: any): string => {
  if (input === null || input === undefined) {
    return 'null';
  }
  
  let sanitized = String(input);
  
  // Remove or encode potentially dangerous characters
  sanitized = sanitized
    .replace(/\r\n/g, '\\r\\n')  // Replace CRLF
    .replace(/\n/g, '\\n')      // Replace LF
    .replace(/\r/g, '\\r')      // Replace CR
    .replace(/\t/g, '\\t')      // Replace tabs
    .replace(/\x00/g, '\\x00')  // Replace null bytes
    .replace(/\x1b/g, '\\x1b'); // Replace escape sequences
  
  // Truncate if too long to prevent log flooding
  if (sanitized.length > 1000) {
    sanitized = sanitized.substring(0, 1000) + '...[truncated]';
  }
  
  return sanitized;
};

export const safeLog = {
  info: (message: string, data?: any) => {
    console.log(sanitizeForLog(message), data ? sanitizeForLog(data) : '');
  },
  error: (message: string, error?: any) => {
    console.error(sanitizeForLog(message), error ? sanitizeForLog(error) : '');
  },
  warn: (message: string, data?: any) => {
    console.warn(sanitizeForLog(message), data ? sanitizeForLog(data) : '');
  },
  debug: (message: string, data?: any) => {
    if (process.env.NODE_ENV === 'development') {
      console.debug(sanitizeForLog(message), data ? sanitizeForLog(data) : '');
    }
  }
};