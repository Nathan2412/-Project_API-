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

// DELETE request
export async function apiDelete(path, token = null) {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(path, {
    method: 'DELETE',
    headers,
  });
  
  if (res.status === 401 && token) {
    handleUnauthorized();
    throw new Error('Session expirée. Veuillez vous reconnecter.');
  }
  
  if (!res.ok && res.status !== 204) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${res.status}`);
  }
  
  return res.status === 204 ? null : res.json();
}

// PUT request
export async function apiPut(path, data, token = null) {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(path, {
    method: 'PUT',
    headers,
    body: JSON.stringify(data),
  });
  
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

// PATCH request
export async function apiPatch(path, data, token = null) {
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(path, {
    method: 'PATCH',
    headers,
    body: JSON.stringify(data),
  });
  
  if (res.status === 401 && token) {
    handleUnauthorized();
    throw new Error('Session expirée. Veuillez vous reconnecter.');
  }
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    // Gérer les erreurs de validation (format: {"field": ["error1", "error2"]})
    let errorMessage = errorData.detail || errorData.error;
    if (!errorMessage && typeof errorData === 'object') {
      const firstKey = Object.keys(errorData)[0];
      if (firstKey && Array.isArray(errorData[firstKey])) {
        errorMessage = `${firstKey}: ${errorData[firstKey][0]}`;
      } else if (firstKey && typeof errorData[firstKey] === 'string') {
        errorMessage = `${firstKey}: ${errorData[firstKey]}`;
      }
    }
    throw new Error(errorMessage || `HTTP ${res.status}`);
  }
  
  return res.json();
}

// ===== API Endpoints =====

export async function getHealth() {
  return apiGet(`${API_BASE}/health`);
}

export async function getProducts() {
  return apiGet(`${API_BASE}/products`);
}

export async function getRates(base = 'EUR') {
  return apiGet(`${API_BASE}/external/rates?base=${encodeURIComponent(base)}`);
}

export async function getExternalProducts() {
  return apiGet(`${API_BASE}/external/products`);
}

export async function getOrders(token) {
  return apiGet(`${API_BASE}/orders`, token);
}

export async function getOrder(id, token) {
  return apiGet(`${API_BASE}/orders/${id}`, token);
}

export async function createOrder(data, token) {
  return apiPost(`${API_BASE}/orders`, data, token);
}

export async function getCart(token) {
  return apiGet(`${API_BASE}/cart`, token);
}

export async function addToCart(data, token) {
  return apiPost(`${API_BASE}/cart`, data, token);
}

export async function updateCartItem(id, data, token) {
  return apiPut(`${API_BASE}/cart/${id}`, data, token);
}

export async function removeFromCart(id, token) {
  return apiDelete(`${API_BASE}/cart/${id}`, token);
}

export async function createPaymentIntent(orderId, token) {
  return apiPost(`${API_BASE}/payment/create-intent`, { order_id: orderId }, token);
}

export async function updateProfile(data, token) {
  return apiPatch(`${API_BASE}/auth/me`, data, token);
}
