const express = require('express');
const { Op } = require('sequelize');
const Product = require('../models/Product');
const { authMiddleware, adminMiddleware } = require('../middleware/auth');
const router = express.Router();

// GET /api/products - list products with pagination and filters
router.get('/', async (req, res) => {
  try {
    const {
      page = 1,
      limit = 12,
      q,
      minPrice,
      maxPrice,
      sort = 'created_at:desc',
    } = req.query;

    const where = {};
    if (q) {
      where[Op.or] = [
        { name: { [Op.like]: `%${q}%` } },
        { description: { [Op.like]: `%${q}%` } },
      ];
    }
    if (minPrice || maxPrice) {
      where.price = {};
      if (minPrice) where.price[Op.gte] = Number(minPrice);
      if (maxPrice) where.price[Op.lte] = Number(maxPrice);
    }

    const [sortField, sortDirRaw] = String(sort).split(':');
    const sortDir = String(sortDirRaw || 'desc').toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

    const pageNum = Math.max(1, parseInt(page));
    const limitNum = Math.min(100, Math.max(1, parseInt(limit)));
    const offset = (pageNum - 1) * limitNum;

    const { rows, count } = await Product.findAndCountAll({
      where,
      limit: limitNum,
      offset,
      order: [[sortField || 'created_at', sortDir]],
    });

    res.json({
      items: rows,
      page: pageNum,
      limit: limitNum,
      total: count,
      pages: Math.ceil(count / limitNum),
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'DB_ERROR', message: 'Cannot fetch products. Configure DB and run schema.sql' });
  }
});

// POST /api/products - create product (admin)
router.post('/', authMiddleware, adminMiddleware, async (req, res) => {
  try {
    const { name, description, price, stock } = req.body;
    if (!name || price == null) return res.status(400).json({ error: 'VALIDATION', message: 'name and price are required' });
    const product = await Product.create({ name, description, price, stock: stock ?? 0 });
    res.status(201).json(product);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'DB_ERROR', message: 'Cannot create product' });
  }
});

// PUT /api/products/:id - update product (admin)
router.put('/:id', authMiddleware, adminMiddleware, async (req, res) => {
  try {
    const product = await Product.findByPk(req.params.id);
    if (!product) return res.status(404).json({ error: 'NOT_FOUND' });
    const { name, description, price, stock } = req.body;
    if (price !== undefined && isNaN(Number(price))) {
      return res.status(400).json({ error: 'VALIDATION', message: 'price must be a number' });
    }
    await product.update({
      name: name ?? product.name,
      description: description ?? product.description,
      price: price ?? product.price,
      stock: stock ?? product.stock,
    });
    res.json(product);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'DB_ERROR', message: 'Cannot update product' });
  }
});

// DELETE /api/products/:id - delete product (admin)
router.delete('/:id', authMiddleware, adminMiddleware, async (req, res) => {
  try {
    const product = await Product.findByPk(req.params.id);
    if (!product) return res.status(404).json({ error: 'NOT_FOUND' });
    await product.destroy();
    res.status(204).send();
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'DB_ERROR', message: 'Cannot delete product' });
  }
});

// GET /api/products/:id - get product by id
router.get('/:id', async (req, res) => {
  try {
    const product = await Product.findByPk(req.params.id);
    if (!product) return res.status(404).json({ error: 'NOT_FOUND' });
    res.json(product);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'DB_ERROR', message: 'Cannot fetch product' });
  }
});

module.exports = router;
