import { useState, useEffect } from 'react'
import { apiGet } from '../api'
import './CurrencyConverter.css'

const POPULAR_CURRENCIES = [
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'USD', name: 'Dollar US', symbol: '$' },
  { code: 'GBP', name: 'Livre Sterling', symbol: '£' },
  { code: 'CHF', name: 'Franc Suisse', symbol: 'CHF' },
  { code: 'JPY', name: 'Yen Japonais', symbol: '¥' },
  { code: 'CAD', name: 'Dollar Canadien', symbol: 'C$' },
  { code: 'AUD', name: 'Dollar Australien', symbol: 'A$' },
  { code: 'CNY', name: 'Yuan Chinois', symbol: '¥' },
]

function CurrencyConverter({ onClose }) {
  const [amount, setAmount] = useState(100)
  const [fromCurrency, setFromCurrency] = useState('EUR')
  const [toCurrency, setToCurrency] = useState('USD')
  const [rates, setRates] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadRates()
  }, [fromCurrency])

  const loadRates = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiGet(`/api/external/rates/?base=${fromCurrency}`)
      setRates(data.rates)
    } catch (err) {
      setError('Impossible de charger les taux de change')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const convertedAmount = () => {
    if (!rates || !rates[toCurrency]) return null
    return (amount * rates[toCurrency]).toFixed(2)
  }

  const swapCurrencies = () => {
    setFromCurrency(toCurrency)
    setToCurrency(fromCurrency)
  }

  const getCurrencySymbol = (code) => {
    const currency = POPULAR_CURRENCIES.find(c => c.code === code)
    return currency?.symbol || code
  }

  return (
    <div className="currency-overlay" onClick={onClose}>
      <div className="currency-modal" onClick={e => e.stopPropagation()}>
        <div className="currency-header">
          <h2>💱 Convertisseur de Devises</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="currency-content">
          {error && (
            <div className="error-message">
              ⚠️ {error}
              <button onClick={loadRates}>Réessayer</button>
            </div>
          )}

          <div className="converter-form">
            <div className="input-group">
              <label>Montant</label>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
                min="0"
                step="0.01"
              />
            </div>

            <div className="currency-selectors">
              <div className="input-group">
                <label>De</label>
                <select 
                  value={fromCurrency} 
                  onChange={(e) => setFromCurrency(e.target.value)}
                >
                  {POPULAR_CURRENCIES.map(c => (
                    <option key={c.code} value={c.code}>
                      {c.symbol} {c.code} - {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <button className="swap-btn" onClick={swapCurrencies} title="Inverser">
                ⇄
              </button>

              <div className="input-group">
                <label>Vers</label>
                <select 
                  value={toCurrency} 
                  onChange={(e) => setToCurrency(e.target.value)}
                >
                  {POPULAR_CURRENCIES.map(c => (
                    <option key={c.code} value={c.code}>
                      {c.symbol} {c.code} - {c.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {loading ? (
              <div className="loading">
                <div className="spinner"></div>
                <span>Chargement des taux...</span>
              </div>
            ) : (
              <div className="result">
                <div className="result-amount">
                  <span className="from">
                    {getCurrencySymbol(fromCurrency)} {amount.toFixed(2)}
                  </span>
                  <span className="equals">=</span>
                  <span className="to">
                    {getCurrencySymbol(toCurrency)} {convertedAmount() || '---'}
                  </span>
                </div>
                
                {rates && rates[toCurrency] && (
                  <div className="rate-info">
                    1 {fromCurrency} = {rates[toCurrency].toFixed(4)} {toCurrency}
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="rates-table">
            <h3>Taux de change depuis {fromCurrency}</h3>
            {loading ? (
              <p>Chargement...</p>
            ) : rates ? (
              <div className="rates-grid">
                {POPULAR_CURRENCIES.filter(c => c.code !== fromCurrency).map(c => (
                  <div 
                    key={c.code} 
                    className={`rate-item ${c.code === toCurrency ? 'selected' : ''}`}
                    onClick={() => setToCurrency(c.code)}
                  >
                    <span className="rate-code">{c.symbol} {c.code}</span>
                    <span className="rate-value">
                      {rates[c.code] ? rates[c.code].toFixed(4) : 'N/A'}
                    </span>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CurrencyConverter
