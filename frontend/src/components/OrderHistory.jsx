import { useState, useEffect } from 'react'
import { apiGet } from '../api'
import './OrderHistory.css'

function OrderHistory({ token, onClose }) {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedOrder, setSelectedOrder] = useState(null)

  useEffect(() => {
    loadOrders()
  }, [])

  const loadOrders = async () => {
    try {
      setLoading(true)
      const data = await apiGet('/api/orders/', token)
      setOrders(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadOrderDetails = async (orderId) => {
    try {
      const data = await apiGet(`/api/orders/${orderId}/`, token)
      setSelectedOrder(data)
    } catch (err) {
      setError(err.message)
    }
  }

  const getStatusBadge = (status) => {
    const statusMap = {
      'pending': { label: 'En attente', class: 'status-pending' },
      'paid': { label: 'Payée', class: 'status-paid' },
      'shipped': { label: 'Expédiée', class: 'status-shipped' },
      'delivered': { label: 'Livrée', class: 'status-delivered' },
      'cancelled': { label: 'Annulée', class: 'status-cancelled' },
    }
    const statusInfo = statusMap[status] || { label: status, class: '' }
    return <span className={`status-badge ${statusInfo.class}`}>{statusInfo.label}</span>
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="order-history-overlay" onClick={onClose}>
      <div className="order-history-modal" onClick={e => e.stopPropagation()}>
        <div className="order-history-header">
          <h2>📦 Mes Commandes</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="order-history-content">
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Chargement des commandes...</p>
            </div>
          ) : error ? (
            <div className="error-state">
              <p>❌ {error}</p>
              <button onClick={loadOrders}>Réessayer</button>
            </div>
          ) : orders.length === 0 ? (
            <div className="empty-state">
              <p>🛒 Aucune commande pour le moment</p>
              <p className="hint">Vos commandes apparaîtront ici après votre premier achat.</p>
            </div>
          ) : selectedOrder ? (
            <div className="order-details">
              <button className="back-btn" onClick={() => setSelectedOrder(null)}>
                ← Retour aux commandes
              </button>
              
              <div className="order-detail-header">
                <h3>Commande #{selectedOrder.id}</h3>
                {getStatusBadge(selectedOrder.status)}
              </div>
              
              <p className="order-date">
                Passée le {formatDate(selectedOrder.created_at)}
              </p>

              <div className="order-items-list">
                <h4>Articles commandés</h4>
                {selectedOrder.items?.map((item, index) => (
                  <div key={index} className="order-item">
                    <img 
                      src={item.product?.image || 'https://via.placeholder.com/60'} 
                      alt={item.product?.title || 'Produit'}
                      className="order-item-image"
                    />
                    <div className="order-item-info">
                      <span className="item-title">{item.product?.title || `Produit #${item.product_id}`}</span>
                      <span className="item-quantity">Quantité: {item.quantity}</span>
                      <span className="item-price">{parseFloat(item.price).toFixed(2)} €</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="order-total">
                <span>Total:</span>
                <span className="total-amount">{parseFloat(selectedOrder.total).toFixed(2)} €</span>
              </div>
            </div>
          ) : (
            <div className="orders-list">
              {orders.map(order => (
                <div 
                  key={order.id} 
                  className="order-card"
                  onClick={() => loadOrderDetails(order.id)}
                >
                  <div className="order-card-header">
                    <span className="order-id">Commande #{order.id}</span>
                    {getStatusBadge(order.status)}
                  </div>
                  <div className="order-card-info">
                    <span className="order-date">{formatDate(order.created_at)}</span>
                    <span className="order-total">{parseFloat(order.total).toFixed(2)} €</span>
                  </div>
                  <div className="order-card-footer">
                    <span className="items-count">
                      {order.items_count || order.items?.length || 0} article(s)
                    </span>
                    <span className="view-details">Voir détails →</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default OrderHistory
