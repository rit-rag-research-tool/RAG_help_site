const express = require('express');
const bodyParser = require('body-parser');
require('dotenv').config();

const ragRouter = require('./routes/rag');
const { logRequest, validateQuery } = require('./utils/utils');

const app = express();
app.use(bodyParser.json());

// Logging middleware
app.use((req, res, next) => {
  logRequest(req);
  next();
});

// Validation middleware for /rag route
app.use('/rag', (req, res, next) => {
  if (!validateQuery(req.body.query)) {
    return res.status(400).json({ error: 'Invalid query' });
  }
  next();
});

app.use('/rag', ragRouter);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Node server running on port ${PORT}`);
});