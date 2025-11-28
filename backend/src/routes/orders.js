const express = require('express');
const Joi = require('joi');
const Order = require('../models/Order');
const OrderItem = require('../models/OrderItem');
const Product = require('../models/Product');
const { authMiddleware } = require('../middleware/auth');
const { sequelize } = require('../db');

const router = express.Router();

// Schéma de validation pour créer une commande
const createOrderSchema = Joi.object({
  items: Joi.array().items(
    Joi.object({
      product_id: Joi.number().integer().required(),
      quantity: Joi.number().integer().min(1).required(),
    })
  ).min(1).required(),
});

// POST /api/orders - Créer une commande (protégé)
router.post('/', authMiddleware, async (req, res) => {
  const transaction = await sequelize.transaction();
  
  try {
    const { error, value } = createOrderSchema.validate(req.body);
    if (error) return res.status(400).json({ error: 'VALIDATION', message: error.details[0].message });

    const { items } = value;
    let total = 0;

    // Vérifier la disponibilité des produits et calculer le total
    const productsData = [];
    for (const item of items) {
      const product = await Product.findByPk(item.product_id, { transaction });
      if (!product) {
        await transaction.rollback();
        return res.status(404).json({ error: 'PRODUCT_NOT_FOUND', message: `Produit ${item.product_id} introuvable` });
      }
      if (product.stock < item.quantity) {
        await transaction.rollback();
        return res.status(400).json({ error: 'INSUFFICIENT_STOCK', message: `Stock insuffisant pour ${product.name}` });
      }
      productsData.push({ product, quantity: item.quantity });
      total += parseFloat(product.price) * item.quantity;
    }

    // Créer la commande
    const order = await Order.create({
      user_id: req.user.id,
      total: total.toFixed(2),
      status: 'pending',
    }, { transaction });

    // Créer les lignes de commande et décrémenter le stock
    for (const { product, quantity } of productsData) {
      await OrderItem.create({
        order_id: order.id,
        product_id: product.id,
        quantity,
        price: product.price,
      }, { transaction });

      // Décrémenter le stock
      product.stock -= quantity;
      await product.save({ transaction });
    }

    await transaction.commit();

    // Récupérer la commande avec les items
    const fullOrder = await Order.findByPk(order.id, {
      include: [{
        model: OrderItem,
        include: [Product],
      }],
    });

    res.status(201).json(fullOrder);
  } catch (err) {
    await transaction.rollback();
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR', message: 'Erreur lors de la création de la commande' });
  }
});

// GET /api/orders - Récupérer les commandes de l'utilisateur connecté
router.get('/', authMiddleware, async (req, res) => {
  try {
    const orders = await Order.findAll({
      where: { user_id: req.user.id },
      include: [{
        model: OrderItem,
        include: [Product],
      }],
      order: [['id', 'DESC']],
    });
    res.json(orders);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR' });
  }
});

// GET /api/orders/:id - Récupérer une commande spécifique
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const order = await Order.findOne({
      where: { id: req.params.id, user_id: req.user.id },
      include: [{
        model: OrderItem,
        include: [Product],
      }],
    });
    if (!order) return res.status(404).json({ error: 'ORDER_NOT_FOUND' });
    res.json(order);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR' });
  }
});

module.exports = router;
