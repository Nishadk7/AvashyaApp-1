// Avashya Drop - Web Tier Dynamic API Configuration
// -------------------------------------------------------------
// LOCAL TESTING:
// Leaves host as auto-detected hostname (127.0.0.1 or localhost).
//
// AWS EC2 DEPLOYMENT:
// Set APP_EC2_HOST to your App EC2 Instance's Public IP or Public DNS.
// Example: const APP_EC2_HOST = '54.210.12.34';
// -------------------------------------------------------------

const APP_EC2_HOST = window.location.hostname || '127.0.0.1';
const API_PORT = '8000';

window.API_BASE = `http://${APP_EC2_HOST}:${API_PORT}/api`;

console.log('[Avashya Drop Web Tier] Configured REST API Endpoint:', window.API_BASE);
