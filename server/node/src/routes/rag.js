const express = require('express');
const router = express.Router();
const axios = require('axios');

router.post('/', async (req, res) => {
  const { query } = req.body;
  try {
    const response = await axios.post(process.env.PYTHON_API_URL + '/rag', { query });
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Python backend error', details: error.message });
  }
});

module.exports = router;