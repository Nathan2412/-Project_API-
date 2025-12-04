// Sécurité: Fonction d'appel API avec gestion des tokens
const API_BASE = '/api';

// Fonction pour vérifier et nettoyer les tokens invalides
const handleUnauthorized = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  // Recharger pour réinitialiser l'état
  window.location.reload();
};

export async function apiGet(path, token = null) {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  // Sécurité: Ajouter le token JWT si disponible
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(path, { headers });
  
  // Token invalide ou expiré
  if (res.status === 401 && token) {
    handleUnauthorized();
    throw new Error('Session expirée. Veuillez vous reconnecter.');
  }
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${res.status}`);
  }
  
  return res.json();
}

export async function apiPost(path, data, token = null) {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  // Sécurité: Ajouter le token JWT si disponible
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(path, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  });
  
  // Token invalide ou expiré (sauf pour login/register)
  if (res.status === 401 && token && !path.includes('/auth/login') && !path.includes('/auth/register')) {
    handleUnauthorized();
    throw new Error('Session expirée. Veuillez vous reconnecter.');
  }
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    // Extraire le message d'erreur de différents formats
    let errorMessage = errorData.detail || errorData.error;
    if (!errorMessage && typeof errorData === 'object') {
      // Gérer les erreurs de validation (format: {"field": ["error1", "error2"]})
      const firstKey = Object.keys(errorData)[0];
      if (firstKey && Array.isArray(errorData[firstKey])) {
        errorMessage = `${firstKey}: ${errorData[firstKey][0]}`;
      }
    }
    throw new Error(errorMessage || `HTTP ${res.status}`);
  }
  
  return res.json();
}

export async function getHealth() {
  return apiGet(`${API_BASE}/health`);
}

export async function getProducts() {
  return apiGet(`${API_BASE}/products`);
}

export async function getRates(base = 'EUR') {
  return apiGet(`${API_BASE}/external/rates?base=${encodeURIComponent(base)}`);
}
