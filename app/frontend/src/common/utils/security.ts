/**
 * Frontend security utilities
 */

// Input sanitization
export const sanitizeInput = (input: string): string => {
  if (!input) return '';
  
  // Remove dangerous characters and patterns
  return input
    .replace(/<script[^>]*>.*?<\/script>/gi, '')
    .replace(/<[^>]*>/g, '')
    .replace(/javascript:/gi, '')
    .replace(/vbscript:/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .trim()
    .substring(0, 1000); // Limit length
};

// File validation
export const validateFile = (file: File): { valid: boolean; error?: string } => {
  const maxSize = parseInt(import.meta.env.VITE_MAX_FILE_SIZE) || 10485760; // 10MB
  const allowedTypes = (import.meta.env.VITE_ALLOWED_FILE_TYPES || 'pdf,jpg,jpeg,png,doc,docx').split(',');
  
  if (file.size > maxSize) {
    return { valid: false, error: 'File size exceeds limit' };
  }
  
  const fileExtension = file.name.split('.').pop()?.toLowerCase();
  if (!fileExtension || !allowedTypes.includes(fileExtension)) {
    return { valid: false, error: 'File type not allowed' };
  }
  
  return { valid: true };
};

// URL validation
export const isValidUrl = (url: string): boolean => {
  try {
    const urlObj = new URL(url);
    return urlObj.protocol === 'https:' || urlObj.protocol === 'http:';
  } catch {
    return false;
  }
};

// XSS protection for display
export const escapeHtml = (text: string): string => {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
};

// Credential encoding for secure transmission
export const encodeCredentials = (username: string, password: string): string => {
  return btoa(`${username}:${password}`);
};

// Hash string utility
export const hashString = async (input: string): Promise<string> => {
  const encoder = new TextEncoder();
  const data = encoder.encode(input);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
};

// Client fingerprinting
export const getClientFingerprint = (): string => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  ctx?.fillText('fingerprint', 10, 10);
  const canvasFingerprint = canvas.toDataURL();
  
  const fingerprint = [
    navigator.userAgent,
    navigator.language,
    screen.width + 'x' + screen.height,
    new Date().getTimezoneOffset(),
    canvasFingerprint.slice(-50)
  ].join('|');
  
  return btoa(fingerprint).slice(0, 32);
};

// Login rate limiter
class LoginRateLimiter {
  private attempts: Map<string, { count: number; lastAttempt: number; lockoutUntil?: number }> = new Map();
  private readonly maxAttempts = 5;
  private readonly lockoutDuration = 15 * 60 * 1000; // 15 minutes
  private readonly resetWindow = 60 * 60 * 1000; // 1 hour

  canAttemptLogin(clientId: string): boolean {
    const now = Date.now();
    const record = this.attempts.get(clientId);
    
    if (!record) return true;
    
    // Check if still locked out
    if (record.lockoutUntil && now < record.lockoutUntil) {
      return false;
    }
    
    // Reset if window has passed
    if (now - record.lastAttempt > this.resetWindow) {
      this.attempts.delete(clientId);
      return true;
    }
    
    return record.count < this.maxAttempts;
  }

  recordAttempt(clientId: string, success: boolean): void {
    const now = Date.now();
    const record = this.attempts.get(clientId) || { count: 0, lastAttempt: now };
    
    if (success) {
      this.attempts.delete(clientId);
      return;
    }
    
    record.count++;
    record.lastAttempt = now;
    
    if (record.count >= this.maxAttempts) {
      record.lockoutUntil = now + this.lockoutDuration;
    }
    
    this.attempts.set(clientId, record);
  }

  getRemainingLockoutTime(clientId: string): number {
    const record = this.attempts.get(clientId);
    if (!record?.lockoutUntil) return 0;
    return Math.max(0, record.lockoutUntil - Date.now());
  }
}

export const loginRateLimiter = new LoginRateLimiter();

// Rate limiting helper
export class RateLimiter {
  private requests: Map<string, number[]> = new Map();
  
  isAllowed(key: string, maxRequests: number = 10, windowMs: number = 60000): boolean {
    const now = Date.now();
    const requests = this.requests.get(key) || [];
    
    // Remove old requests outside the window
    const validRequests = requests.filter(time => now - time < windowMs);
    
    if (validRequests.length >= maxRequests) {
      return false;
    }
    
    validRequests.push(now);
    this.requests.set(key, validRequests);
    return true;
  }
}