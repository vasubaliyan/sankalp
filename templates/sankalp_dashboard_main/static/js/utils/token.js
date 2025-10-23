// token.js — generates random tokens for session simulation
export function generateSessionToken(length = 32) {
  const array = new Uint8Array(length);
  crypto.getRandomValues(array); // secure random bytes
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}
