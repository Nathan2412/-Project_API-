const express = require('express');
const Joi = require('joi');
const User = require('../models/User');
const { hashPassword, comparePassword, generateToken } = require('../utils/auth');

const router = express.Router();

// Schéma de validation
const registerSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(6).required(),
  name: Joi.string().optional(),
});

const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required(),
});

// POST /api/auth/register - Inscription
router.post('/register', async (req, res) => {
  try {
    const { error, value } = registerSchema.validate(req.body);
    if (error) return res.status(400).json({ error: 'VALIDATION', message: error.details[0].message });

    const { email, password, name } = value;

    // Vérifier si l'utilisateur existe déjà
    const existing = await User.findOne({ where: { email } });
    if (existing) {
      return res.status(409).json({ error: 'USER_EXISTS', message: 'Cet email est déjà utilisé' }); //todo : trouver ujn message d'erreur plus généric, celui ci donne trop d'info
    }

    // Hash du mot de passe
    const hashedPassword = await hashPassword(password);

    //TODO; verifier que l'email est au bon format : @ . et domaine sous 3 lettre

    // Créer l'utilisateur
    const user = await User.create({
      email,
      password: hashedPassword,
      name: name || null,
      role: 'user',
    });

    // Générer le token
    const token = generateToken({ id: user.id, email: user.email, role: user.role });

    res.status(201).json({
      token,
      user: { id: user.id, email: user.email, name: user.name, role: user.role },
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR', message: 'Erreur lors de l\'inscription' });
  }
});

// POST /api/auth/login - Connexion
router.post('/login', async (req, res) => {
  try {
    const { error, value } = loginSchema.validate(req.body);
    if (error) return res.status(400).json({ error: 'VALIDATION', message: error.details[0].message });

    const { email, password } = value;

    // Trouver l'utilisateur
    const user = await User.findOne({ where: { email } });
    if (!user) {
      return res.status(401).json({ error: 'INVALID_CREDENTIALS', message: 'Email ou mot de passe incorrect' });
    }

    // Vérifier le mot de passe
    const isValid = await comparePassword(password, user.password);
    if (!isValid) {
      return res.status(401).json({ error: 'INVALID_CREDENTIALS', message: 'Email ou mot de passe incorrect' });
    }

    // Générer le token
    const token = generateToken({ id: user.id, email: user.email, role: user.role });

    res.json({
      token,
      user: { id: user.id, email: user.email, name: user.name, role: user.role },
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR', message: 'Erreur lors de la connexion' });
  }
});

// GET /api/auth/me - Profil utilisateur (protégé)
const { authMiddleware } = require('../middleware/auth');
router.get('/me', authMiddleware, async (req, res) => {
  try {
    const user = await User.findByPk(req.user.id, {
      attributes: ['id', 'email', 'name', 'role'],
    });
    if (!user) return res.status(404).json({ error: 'USER_NOT_FOUND' });
    res.json(user);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'SERVER_ERROR' });
  }
});

module.exports = router;
