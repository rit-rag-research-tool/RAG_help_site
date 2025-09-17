function validateQuery(query) {
  // Checks if query is a non-empty string
  return typeof query === 'string' && query.trim().length > 0;
}

function logRequest(req) {
  // Simple request logger
  console.log(`Received request: ${JSON.stringify(req.body)}`);
}

module.exports = {
  validateQuery,
  logRequest
};