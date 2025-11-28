require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { sequelize } = require('./db');
const productsRouter = require('./routes/products');
const externalRouter = require('./routes/external');
const authRouter = require('./routes/auth');
const ordersRouter = require('./routes/orders');
const cartRouter = require('./routes/cart');
const payment = require('./routes/payment');

const app = express();

// Webhook Stripe doit être traité AVANT express.json()
app.post('/api/payment/webhook', express.raw({ type: 'application/json' }), payment.webhookHandler);

app.use(express.json());
// En dev, on autorise toutes origines car le frontend utilise le proxy Vite
app.use(cors());

// Health check
app.get('/api/health', async (req, res) => {
	try {
		await sequelize.authenticate();
		res.json({ ok: true, db: 'connected' });
	} catch {
		res.json({ ok: true, db: 'disconnected' });
	}
});

// API routes
app.use('/api/auth', authRouter);
app.use('/api/products', productsRouter);
app.use('/api/orders', ordersRouter);
app.use('/api/cart', cartRouter);
app.use('/api/payment', payment.router);
app.use('/api/external', externalRouter);

const PORT = process.env.PORT || 5000;
async function start() {
	try {
		await sequelize.authenticate();
		console.log('DB connected');
	} catch (e) {
		console.warn('DB not connected yet. Configure .env and run db/schema.sql');
	}
	return app.listen(PORT, () => console.log(`Server listening on ${PORT}`));
}

if (process.env.NODE_ENV !== 'test') {
	start();
}

module.exports = { app, start };
