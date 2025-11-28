const express = require('express');
// Stripe SDK chargé paresseusement uniquement si clé disponible
let stripeFactory = null;
try { stripeFactory = require('stripe'); } catch { stripeFactory = null; }
const Order = require('../models/Order');
const { authMiddleware } = require('../middleware/auth');

const router = express.Router();

function getStripe() {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) return null;
  if (!stripeFactory) return null;
  try { return stripeFactory(key); } catch { return null; }
}

// POST /api/payment/create-intent - Créer un Payment Intent Stripe
router.post('/create-intent', authMiddleware, async (req, res) => {
  try {
    const stripe = getStripe();
    if (!stripe) return res.status(500).json({ error: 'STRIPE_CONFIG', message: 'STRIPE_SECRET_KEY manquant' });
    const { order_id } = req.body;

    if (!order_id) {
      return res.status(400).json({ error: 'VALIDATION', message: 'order_id requis' });
    }

    // Récupérer la commande
    const order = await Order.findOne({
      where: { id: order_id, user_id: req.user.id },
    });

    if (!order) {
      return res.status(404).json({ error: 'ORDER_NOT_FOUND', message: 'Commande introuvable' });
    }

    if (order.status === 'paid') {
      return res.status(400).json({ error: 'ALREADY_PAID', message: 'Cette commande a déjà été payée' });
    }

    // Créer le Payment Intent
    const paymentIntent = await stripe.paymentIntents.create({
      amount: Math.round(parseFloat(order.total) * 100), // Montant en centimes
      currency: 'eur',
      metadata: {
        order_id: order.id,
        user_id: req.user.id,
      },
    });

    res.json({
      clientSecret: paymentIntent.client_secret,
      paymentIntentId: paymentIntent.id,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'STRIPE_ERROR', message: err.message });
  }
});

// POST /api/payment/webhook - Webhook Stripe pour confirmer le paiement
async function webhookHandler(req, res) {
  const stripe = getStripe();
  if (!stripe) return res.status(500).json({ error: 'STRIPE_CONFIG', message: 'STRIPE_SECRET_KEY manquant' });
  const sig = req.headers['stripe-signature'];
  const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

  let event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Gérer l'événement
  if (event.type === 'payment_intent.succeeded') {
    const paymentIntent = event.data.object;
    const orderId = paymentIntent.metadata.order_id;

    // Mettre à jour le statut de la commande
    const order = await Order.findByPk(orderId);
    if (order) {
      order.status = 'paid';
      await order.save();
      console.log(`Commande ${orderId} marquée comme payée`);
    }
  }

  res.json({ received: true });
}

// POST /api/payment/confirm - Confirmation manuelle (dev uniquement)
router.post('/confirm', authMiddleware, async (req, res) => {
  try {
    const { order_id } = req.body;

    const order = await Order.findOne({
      where: { id: order_id, user_id: req.user.id },
    });

    if (!order) {
      return res.status(404).json({ error: 'ORDER_NOT_FOUND' });
    }

    order.status = 'paid';
    await order.save();

    res.json({ message: 'Paiement confirmé', order });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR' });
  }
});

module.exports = router;
module.exports.router = router;
module.exports.webhookHandler = webhookHandler;
