// Run this in browser console to check auth state
console.log('=== AUTH DEBUG ===');
console.log('Token:', localStorage.getItem('token'));
console.log('Project ID:', localStorage.getItem('projectId'));
console.log('Username:', localStorage.getItem('username'));
console.log('User Type:', localStorage.getItem('usertype'));
console.log('Django User Type:', localStorage.getItem('django_user_type'));
console.log('Token Expiry:', localStorage.getItem('tokenExpiry'));

// Check if token is expired
const expiry = localStorage.getItem('tokenExpiry');
if (expiry) {
  const expiryTime = new Date(expiry);
  const now = new Date();
  console.log('Token expires:', expiryTime);
  console.log('Current time:', now);
  console.log('Token expired:', expiryTime < now);
}