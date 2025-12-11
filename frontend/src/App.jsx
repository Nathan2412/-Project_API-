

import { useEffect, useState } from 'react'
import './App.css'
import { getProducts, apiPost, apiGet } from './api'
import OrderHistory from './components/OrderHistory'
import CurrencyConverter from './components/CurrencyConverter'
import ProfileModal from './components/ProfileModal'

// Sécurité: Sanitize les entrées utilisateur
const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input
  return input.replace(/[<>]/g, '').trim()
}

function App() {
  const [products, setProducts] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  
  // Panier (stocké en localStorage pour persistance)
  const [cart, setCart] = useState(() => {
    const saved = localStorage.getItem('cart')
    return saved ? JSON.parse(saved) : []
  })
  const [cartOpen, setCartOpen] = useState(false)
  
  // Authentification
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [authModal, setAuthModal] = useState(null) // 'login' | 'register' | null
  const [authForm, setAuthForm] = useState({ username: '', email: '', password: '' })
  const [authError, setAuthError] = useState('')
  const [authLoading, setAuthLoading] = useState(false)
  
  // Toast notifications
  const [toast, setToast] = useState(null)
  
  // Modales additionnelles
  const [showOrders, setShowOrders] = useState(false)
  const [showCurrency, setShowCurrency] = useState(false)
  const [showProfile, setShowProfile] = useState(false)

  // Sauvegarder le panier dans localStorage
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart))
  }, [cart])

  useEffect(() => {
    loadProducts()
  }, [])

  const showToast = (message, isError = false) => {
    setToast({ message, isError })
    setTimeout(() => setToast(null), 3000)
  }

  const loadProducts = async () => {
    setError(null)
    setLoading(true)
    try {
      const data = await getProducts()
      setProducts(data)
    } catch (e) {
      setError('Impossible de récupérer les produits.')
    } finally {
      setLoading(false)
    }
  }

  // ===== PANIER =====
  const addToCart = (product) => {
    if (product.stock === 0) return
    
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id)
      if (existing) {
        // Vérification sécurité: ne pas dépasser le stock
        if (existing.quantity >= product.stock) {
          showToast('Stock maximum atteint!', true)
          return prev
        }
        return prev.map(item => 
          item.id === product.id 
            ? { ...item, quantity: item.quantity + 1 }
            : item
        )
      }
      return [...prev, { ...product, quantity: 1 }]
    })
    showToast(`${product.title} ajouté au panier!`)
  }

  const updateQuantity = (productId, delta) => {
    setCart(prev => {
      return prev.map(item => {
        if (item.id !== productId) return item
        const newQty = item.quantity + delta
        // Sécurité: quantité entre 1 et stock disponible
        if (newQty < 1) return item
        const product = products.find(p => p.id === productId)
        if (product && newQty > product.stock) {
          showToast('Stock maximum atteint!', true)
          return item
        }
        return { ...item, quantity: newQty }
      })
    })
  }

  const removeFromCart = (productId) => {
    setCart(prev => prev.filter(item => item.id !== productId))
    showToast('Produit retiré du panier')
  }

  const cartTotal = cart.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0)
  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0)

  // ===== AUTHENTIFICATION =====
  const handleAuthSubmit = async (e) => {
    e.preventDefault()
    setAuthError('')
    setAuthLoading(true)

    const username = sanitizeInput(authForm.username)
    const email = sanitizeInput(authForm.email)
    const password = authForm.password

    try {
      if (authModal === 'register') {
        // Inscription
        await apiPost('/api/auth/register/', { username, email, password })
        showToast('Compte créé! Connectez-vous.')
        setAuthModal('login')
        setAuthForm({ username: '', email: '', password: '' })
      } else {
        // Connexion - utilise EMAIL comme identifiant
        const response = await apiPost('/api/auth/login/', { email, password })
        
        localStorage.setItem('token', response.access)
        localStorage.setItem('refreshToken', response.refresh)
        setToken(response.access)
        
        // Récupérer les infos utilisateur
        const userData = await apiGet('/api/auth/me/', response.access)
        localStorage.setItem('user', JSON.stringify(userData))
        setUser(userData)
        
        setAuthModal(null)
        setAuthForm({ username: '', email: '', password: '' })
        showToast(`Bienvenue, ${userData.username}!`)
      }
    } catch (err) {
      setAuthError(err.message || 'Erreur de connexion')
    } finally {
      setAuthLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
    showToast('Déconnexion réussie')
  }

  // ===== COMMANDE =====
  const handleCheckout = async () => {
    if (!user) {
      setAuthModal('login')
      showToast('Connectez-vous pour commander', true)
      return
    }

    if (cart.length === 0) {
      showToast('Votre panier est vide', true)
      return
    }

    try {
      // Créer la commande via l'API sécurisée
      const orderData = {
        items: cart.map(item => ({
          product_id: item.id,
          quantity: item.quantity
        })),
        total: cartTotal
      }

      await apiPost('/api/orders/', orderData, token)
      
      // Vider le panier après commande réussie
      setCart([])
      setCartOpen(false)
      showToast('🎉 Commande passée avec succès!')
    } catch (err) {
      showToast('Erreur lors de la commande: ' + err.message, true)
    }
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <h1>🛍️ Ma Boutique</h1>
            <p className="tagline">Découvrez nos produits exceptionnels</p>
          </div>
          <div className="header-right">
            {/* Bouton convertisseur de devises */}
            <button className="tool-btn" onClick={() => setShowCurrency(true)} title="Convertisseur de devises">
              💱
            </button>
            
            <button className="cart-btn" onClick={() => setCartOpen(true)}>
              🛒 Panier
              {cartCount > 0 && <span className="cart-count">{cartCount}</span>}
            </button>
            
            {user ? (
              <div className="user-info">
                <span>👤 {user.username}</span>
                <button className="profile-btn" onClick={() => setShowProfile(true)} title="Mon profil">⚙️</button>
                <button className="orders-btn" onClick={() => setShowOrders(true)}>📦 Commandes</button>
                <button className="logout-btn" onClick={logout}>Déconnexion</button>
              </div>
            ) : (
              <button className="auth-btn" onClick={() => setAuthModal('login')}>
                Connexion
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <section className="products-section">
          <div className="section-header">
            <h2>Nos Produits</h2>
            <div className="section-actions">
              <button className="refresh-btn" onClick={loadProducts}>
                🔄 Rafraîchir
              </button>
            </div>
          </div>

          {error && <p className="error-message">{error}</p>}
          
          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              <p>Chargement des produits...</p>
            </div>
          ) : products.length > 0 ? (
            <div className="products-grid">
              {products.map(p => (
                <div key={p.id} className="product-card">
                  <div className="product-image-container">
                    <img 
                      src={p.image || 'https://via.placeholder.com/300x200?text=Produit'} 
                      alt={p.title}
                      className="product-image"
                      onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/300x200?text=Image+non+disponible'
                      }}
                    />
                    {p.stock <= 3 && p.stock > 0 && (
                      <span className="stock-badge low">Plus que {p.stock}!</span>
                    )}
                    {p.stock === 0 && (
                      <span className="stock-badge out">Rupture</span>
                    )}
                  </div>
                  <div className="product-info">
                    <h3 className="product-title">{p.title}</h3>
                    <p className="product-description">{p.description}</p>
                    <div className="product-footer">
                      <span className="product-price">{parseFloat(p.price).toFixed(2)} €</span>
                      <span className="product-stock">Stock: {p.stock}</span>
                    </div>
                    <button 
                      className={`add-to-cart-btn ${cart.find(item => item.id === p.id) ? 'added' : ''}`}
                      onClick={() => addToCart(p)}
                      disabled={p.stock === 0}
                    >
                      {p.stock === 0 
                        ? 'Indisponible' 
                        : cart.find(item => item.id === p.id) 
                          ? '✓ Dans le panier' 
                          : '🛒 Ajouter au panier'
                      }
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>🏪 Aucun produit disponible pour le moment.</p>
            </div>
          )}
        </section>
      </main>

      {/* Cart Sidebar */}
      <div className={`cart-overlay ${cartOpen ? 'open' : ''}`} onClick={() => setCartOpen(false)} />
      <div className={`cart-sidebar ${cartOpen ? 'open' : ''}`}>
        <div className="cart-header">
          <h2>🛒 Mon Panier</h2>
          <button className="close-cart-btn" onClick={() => setCartOpen(false)}>✕</button>
        </div>
        
        <div className="cart-items">
          {cart.length === 0 ? (
            <div className="cart-empty">
              <p>Votre panier est vide</p>
            </div>
          ) : (
            cart.map(item => (
              <div key={item.id} className="cart-item">
                <img 
                  src={item.image || 'https://via.placeholder.com/80'} 
                  alt={item.title}
                  className="cart-item-image"
                />
                <div className="cart-item-info">
                  <div className="cart-item-title">{item.title}</div>
                  <div className="cart-item-price">{parseFloat(item.price).toFixed(2)} €</div>
                  <div className="cart-item-controls">
                    <button className="qty-btn" onClick={() => updateQuantity(item.id, -1)}>−</button>
                    <span className="cart-item-qty">{item.quantity}</span>
                    <button className="qty-btn" onClick={() => updateQuantity(item.id, 1)}>+</button>
                    <button className="remove-item-btn" onClick={() => removeFromCart(item.id)}>
                      Supprimer
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
        
        <div className="cart-footer">
          <div className="cart-total">
            <span>Total:</span>
            <span>{cartTotal.toFixed(2)} €</span>
          </div>
          <button 
            className="checkout-btn" 
            onClick={handleCheckout}
            disabled={cart.length === 0}
          >
            {user ? '✓ Commander' : '🔐 Se connecter pour commander'}
          </button>
        </div>
      </div>

      {/* Auth Modal */}
      {authModal && (
        <div className="modal-overlay" onClick={() => setAuthModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>{authModal === 'login' ? '🔐 Connexion' : '📝 Inscription'}</h2>
            
            <form onSubmit={handleAuthSubmit}>
              {authModal === 'register' && (
                <div className="form-group">
                  <label>Nom d'utilisateur</label>
                  <input
                    type="text"
                    value={authForm.username}
                    onChange={e => setAuthForm({...authForm, username: e.target.value})}
                    required
                    minLength={3}
                    maxLength={50}
                    autoComplete="username"
                  />
                </div>
              )}
              
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={authForm.email}
                  onChange={e => setAuthForm({...authForm, email: e.target.value})}
                  required
                  autoComplete="email"
                />
              </div>
              
              <div className="form-group">
                <label>Mot de passe</label>
                <input
                  type="password"
                  value={authForm.password}
                  onChange={e => setAuthForm({...authForm, password: e.target.value})}
                  required
                  minLength={4}
                  autoComplete={authModal === 'login' ? 'current-password' : 'new-password'}
                />
              </div>
              
              {authError && <p className="form-error">{authError}</p>}
              
              <button type="submit" className="submit-btn" disabled={authLoading}>
                {authLoading ? 'Chargement...' : authModal === 'login' ? 'Se connecter' : "S'inscrire"}
              </button>
            </form>
            
            <div className="modal-footer">
              {authModal === 'login' ? (
                <p>Pas de compte? <button onClick={() => { setAuthModal('register'); setAuthError('') }}>S'inscrire</button></p>
              ) : (
                <p>Déjà un compte? <button onClick={() => { setAuthModal('login'); setAuthError('') }}>Se connecter</button></p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Order History Modal */}
      {showOrders && user && (
        <OrderHistory 
          token={token} 
          onClose={() => setShowOrders(false)} 
        />
      )}

      {/* Currency Converter Modal */}
      {showCurrency && (
        <CurrencyConverter 
          onClose={() => setShowCurrency(false)} 
        />
      )}

      {/* Profile Modal */}
      {showProfile && user && (
        <ProfileModal
          user={user}
          token={token}
          onClose={() => setShowProfile(false)}
          onUpdate={(updatedUser) => {
            setUser(updatedUser)
            localStorage.setItem('user', JSON.stringify(updatedUser))
            showToast('Profil mis à jour avec succès')
          }}
        />
      )}

      {/* Toast Notification */}
      {toast && (
        <div className={`toast ${toast.isError ? 'error' : ''}`}>
          {toast.message}
        </div>
      )}

      {/* Footer */}
      <footer className="footer">
        <p>© 2025 Ma Boutique - Projet API Sécurisé</p>
      </footer>
    </div>
  )
}

export default App
