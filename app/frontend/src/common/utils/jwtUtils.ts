/**
 * JWT Token utilities for extracting user information
 */

interface JWTPayload {
  username?: string;
  user_type?: string;
  admin_type?: string;
  project_id?: number;
  tenant_id?: string | null;
  is_superadmin?: boolean;
  user_id?: number;
  exp?: number;
  iat?: number;
}

const normalizeUserType = (value?: string | null): string | null => {
  if (!value) return null;
  if (value === 'master' || value === 'MASTER_ADMIN') return 'masteradmin';
  return value;
};

/**
 * Decode JWT token without verification (client-side only)
 * WARNING: This should only be used for extracting non-sensitive data
 */
export const decodeJWT = (token: string): JWTPayload | null => {
  try {
    // JWT tokens have 3 parts separated by dots
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.error('Invalid JWT token format');
      return null;
    }

    // Decode the payload (second part)
    const payload = parts[1];
    
    // Add padding if needed for base64 decoding
    const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
    
    // Decode base64
    const decodedPayload = atob(paddedPayload.replace(/-/g, '+').replace(/_/g, '/'));
    
    // Parse JSON
    const parsedPayload: JWTPayload = JSON.parse(decodedPayload);
    
    return parsedPayload;
  } catch (error) {
    console.error('Error decoding JWT token:', error);
    return null;
  }
};

/**
 * Check if JWT token is expired
 */
export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = decodeJWT(token);
    if (!payload || !payload.exp) {
      return true;
    }

    // JWT exp is in seconds, Date.now() is in milliseconds
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (error) {
    console.error('Error checking token expiration:', error);
    return true;
  }
};

/**
 * Extract user information from JWT token
 */
export const extractUserInfoFromToken = (token: string) => {
  const payload = decodeJWT(token);
  if (!payload) {
    return null;
  }

  return {
    username: payload.username || null,
    usertype: normalizeUserType(payload.user_type),
    django_user_type: normalizeUserType(payload.admin_type),
    userId: payload.user_id || null,
    projectId: payload.project_id || null,
    tenantId: payload.tenant_id || null,
    isSuperAdmin: Boolean(payload.is_superadmin),
  };
};
