'use strict';

module.exports.getExpirationTimestamp = () => {
  // Current timestamp in seconds
  const now = Math.floor(Date.now() / 1000);
  
  // Add 365 days in seconds (365 * 24 * 60 * 60)
  const expirationTimestamp = now + (365 * 24 * 60 * 60);
  
  return expirationTimestamp;
};