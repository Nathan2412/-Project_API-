const express = require('express');
const Joi = require('joi');
const { sequelize } = require('../db');
const CartItem = require('../models/CartItem');
const Product = require('../models/Product');
const Order = require('../models/Order');
const OrderItem = require('../models/OrderItem');
const { authMiddleware } = require('../middleware/auth');

const router = express.Router();

// Get current user's cart
router.get('/', authMiddleware, async (req, res) => {
  try {
    const items = await CartItem.findAll({
      where: { user_id: req.user.id },
      include: [Product],
      order: [['id', 'DESC']],
    });
    const total = items.reduce((sum, it) => sum + Number(it.quantity) * Number(it.Product.price), 0);
    res.json({ items, total: total.toFixed(2) });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR' });
  }
});

// Add item to cart
router.post('/', authMiddleware, async (req, res) => {
  const schema = Joi.object({ product_id: Joi.number().integer().required(), quantity: Joi.number().integer().min(1).default(1) });
  const { error, value } = schema.validate(req.body);
  if (error) return res.status(400).json({ error: 'VALIDATION', message: error.details[0].message });

  try {
    const product = await Product.findByPk(value.product_id);
    if (!product) return res.status(404).json({ error: 'PRODUCT_NOT_FOUND' });

    const [item, created] = await CartItem.findOrCreate({
      where: { user_id: req.user.id, product_id: value.product_id },
      defaults: { quantity: value.quantity },
    });
    if (!created) {
      item.quantity += value.quantity;
      await item.save();
    }
    res.status(created ? 201 : 200).json(item);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR' });
  }
});

// Update item quantity
router.put('/:product_id', authMiddleware, async (req, res) => {
  const schema = Joi.object({ quantity: Joi.number().integer().min(1).required() });
  const { error, value } = schema.validate(req.body);
  if (error) return res.status(400).json({ error: 'VALIDATION', message: error.details[0].message });
  try {
    const item = await CartItem.findOne({ where: { user_id: req.user.id, product_id: req.params.product_id } });
    if (!item) return res.status(404).json({ error: 'NOT_FOUND' });
    item.quantity = value.quantity;
    await item.save();
    res.json(item);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR' });
  }
});

// Remove item
router.delete('/:product_id', authMiddleware, async (req, res) => {
  try {
    const deleted = await CartItem.destroy({ where: { user_id: req.user.id, product_id: req.params.product_id } });
    if (!deleted) return res.status(404).json({ error: 'NOT_FOUND' });
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR' });
  }
});

// Clear cart
router.delete('/', authMiddleware, async (req, res) => {
  try {
    await CartItem.destroy({ where: { user_id: req.user.id } });
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR' });
  }
});

// Create order from cart
router.post('/checkout', authMiddleware, async (req, res) => {
  const transaction = await sequelize.transaction();
  try {
    const items = await CartItem.findAll({
      where: { user_id: req.user.id },
      include: [Product],
      transaction,
      lock: transaction.LOCK.UPDATE,
    });
    if (items.length === 0) {
      await transaction.rollback();
      return res.status(400).json({ error: 'EMPTY_CART' });
    }

    // Validate stock and compute total
    let total = 0;
    for (const it of items) {
      if (it.Product.stock < it.quantity) {
        await transaction.rollback();
        return res.status(400).json({ error: 'INSUFFICIENT_STOCK', message: `Stock insuffisant pour ${it.Product.name}` });
      }
      total += Number(it.quantity) * Number(it.Product.price);
    }

    const order = await Order.create({ user_id: req.user.id, total: total.toFixed(2), status: 'pending' }, { transaction });

    for (const it of items) {
      await OrderItem.create({ order_id: order.id, product_id: it.product_id, quantity: it.quantity, price: it.Product.price }, { transaction });
      it.Product.stock -= it.quantity;
      await it.Product.save({ transaction });
    }

    await CartItem.destroy({ where: { user_id: req.user.id }, transaction });

    await transaction.commit();

    const fullOrder = await Order.findByPk(order.id, { include: [{ model: OrderItem, include: [Product] }] });
    res.status(201).json(fullOrder);
  } catch (err) {
    await transaction.rollback();
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR' });
  }
});

module.exports = router;
