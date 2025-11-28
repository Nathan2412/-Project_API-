const express = require('express');
const axios = require('axios');
const router = express.Router();

// GET /api/external/rates - example of external API integration
router.get('/rates', async (req, res) => {
  try {
    const base = req.query.base || 'EUR';
    const { data } = await axios.get(`https://api.exchangerate.host/latest?base=${encodeURIComponent(base)}`);
    res.json({ base: data.base, date: data.date, rates: data.rates });
  } catch (err) {
    console.error(err);
    res.status(502).json({ error: 'EXTERNAL_API_ERROR', message: 'Failed to fetch currency rates' });
  }
});

module.exports = router;
