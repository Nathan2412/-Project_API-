const { verifyToken } = require('../utils/auth');

function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'UNAUTHORIZED', message: 'Token manquant' });
  }

  const token = authHeader.substring(7);
  const decoded = verifyToken(token);

  if (!decoded) {
    return res.status(401).json({ error: 'INVALID_TOKEN', message: 'Token invalide ou expiré' });
  }

  req.user = decoded; // { id, email, role }
  next();
}

function adminMiddleware(req, res, next) {
  if (!req.user || req.user.role !== 'admin') {
    return res.status(403).json({ error: 'FORBIDDEN', message: 'Accès réservé aux administrateurs' });
  }
  next();
}

module.exports = {
  authMiddleware,
  adminMiddleware,
};
