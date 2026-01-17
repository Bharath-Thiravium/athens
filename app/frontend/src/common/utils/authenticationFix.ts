// Authentication fix utility
import useAuthStore from '../store/authStore';
import refreshToken from './tokenrefresh';

export class AuthenticationFix {
  private static instance: AuthenticationFix;
  private isRefreshing = false;
  private refreshPromise: Promise<string | null> | null = null;

  static getInstance(): AuthenticationFix {
    if (!AuthenticationFix.instance) {
      AuthenticationFix.instance = new AuthenticationFix();
    }
    return AuthenticationFix.instance;
  }

  /**
   * Check if the current token is valid and refresh if needed
   */
  async ensureValidToken(): Promise<string | null> {
    const authState = useAuthStore.getState();
    const currentToken = authState.token;

    if (!currentToken) {
      return null;
    }

    // Check if token is still valid
    if (authState.isAuthenticated()) {
      return currentToken;
    }

    // If already refreshing, return the existing promise
    if (this.isRefreshing && this.refreshPromise) {
      return this.refreshPromise;
    }

    // Start token refresh
    this.isRefreshing = true;
    this.refreshPromise = this.performTokenRefresh();

    try {
      const newToken = await this.refreshPromise;
      return newToken;
    } finally {
      this.isRefreshing = false;
      this.refreshPromise = null;
    }
  }

  private async performTokenRefresh(): Promise<string | null> {
    try {
      const newToken = await refreshToken();
      
      if (newToken) {
        return newToken;
      } else {
        return null;
      }
    } catch (error) {
      return null;
    }
  }

  /**
   * Handle authentication errors from API responses
   */
  handleAuthError(error: any): boolean {
    if (!error.response) return false;

    const status = error.response.status;
    const errorDetail = error.response.data?.detail || '';
    const errorCode = error.response.data?.code || '';

    // Check for token-related errors
    if (status === 401) {
      if (errorDetail.includes('Given token not valid') ||
          errorDetail.includes('Token has expired') ||
          errorDetail.includes('Token is blacklisted') ||
          errorCode === 'token_not_valid') {
        
        useAuthStore.getState().clearToken();
        
        // Redirect to login after a short delay
        setTimeout(() => {
          window.location.replace('/login');
        }, 100);
        
        return true; // Indicates this was an auth error
      }
    }

    return false; // Not an auth error
  }

  /**
   * Get a valid token for WebSocket connections
   */
  async getWebSocketToken(): Promise<string | null> {
    const token = await this.ensureValidToken();
    
    if (!token) {
      return null;
    }

    // Additional validation - decode the token to check expiry
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      const expiryTime = payload.exp;

      if (expiryTime && expiryTime <= currentTime + 60) { // Token expires in less than 1 minute
        return await this.performTokenRefresh();
      }

      return token;
    } catch (error) {
      return token; // Return the token anyway, let the server validate it
    }
  }

  /**
   * Clear all authentication state and redirect to login
   */
  forceLogout(reason: string = 'Authentication failed'): void {
    useAuthStore.getState().clearToken();
    
    // Clear any cached data
    sessionStorage.clear();
    
    // Redirect to login
    window.location.replace('/login');
  }
}

// Export singleton instance
export const authFix = AuthenticationFix.getInstance();