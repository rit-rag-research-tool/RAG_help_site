const express = require('express');
const router = express.Router();
const { generateResponse } = require('../utils/openai');

// Route to handle RAG requests
router.post('/rag', async (req, res) => {
    const { query } = req.body;

    if (!query) {
        return res.status(400).json({ error: 'Query is required' });
    }

    try {
        const response = await generateResponse(query);
        res.json({ response });
    } catch (error) {
        console.error('Error generating response:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

module.exports = router;