

import { useEffect, useState } from 'react'
import './App.css'
import { getHealth, getProducts, getRates } from './api'

function App() {
  const [health, setHealth] = useState(null)
  const [products, setProducts] = useState([])
  const [rates, setRates] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth({ ok: false }))
    getRates('EUR').then(setRates).catch((e) => setError(e.message))
  }, [])

  const loadProducts = async () => {
    setError(null)
    try {
      const data = await getProducts()
      setProducts(data)
    } catch (e) {
      setError('Impossible de récupérer les produits. Configure la base MySQL et exécute db/schema.sql')
    }
  }

  return (
    <div className="container">
      <h1>Boutique en ligne</h1>
      <section>
        <h2>Statut</h2>
        <pre>{JSON.stringify(health, null, 2)}</pre>
      </section>

      <section>
        <h2>Produits</h2>
        <button onClick={loadProducts}>Charger les produits</button>
        {error && <p style={{color: 'crimson'}}>{error}</p>}
        {products.length > 0 ? (
          <ul>
            {products.map(p => (
              <li key={p.id}><strong>{p.name}</strong> — {p.price} € (stock: {p.stock})</li>
            ))}
          </ul>
        ) : (
          <p>Aucun produit (ou DB non configurée).</p>
        )}
      </section>

      <section>
        <h2>Taux de change (API externe)</h2>
        {rates ? (
          <pre>{JSON.stringify({ base: rates.base, sample: { USD: rates.rates?.USD, GBP: rates.rates?.GBP } }, null, 2)}</pre>
        ) : (
          <p>Chargement des taux...</p>
        )}
      </section>
    </div>
  )
}

export default App
