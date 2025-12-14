import { useState, useEffect } from 'react'
import './App.css'

const API_BASE_URL = ''

function App() {
  const [productName, setProductName] = useState('')
  const [reviewText, setReviewText] = useState('')
  const [loading, setLoading] = useState(false)
  const [reviews, setReviews] = useState([])
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState('all')
  const [productFilter, setProductFilter] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [sort, setSort] = useState('created_at_desc')
  const [totalPages, setTotalPages] = useState(1)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  // Fetch reviews on mount
  useEffect(() => {
    fetchReviews()
    fetchStats()
  }, [])

  // Debounced fetch when filters change
  useEffect(() => {
    const handle = setTimeout(() => {
      fetchReviews()
      fetchStats()
    }, 300)
    return () => clearTimeout(handle)
  }, [filter, productFilter, page, pageSize, sort])

  const fetchReviews = async () => {
    try {
      setError(null)
      let url = `${API_BASE_URL}/api/reviews`
      const params = new URLSearchParams()
      
      if (filter !== 'all') {
        params.append('sentiment', filter.toUpperCase())
      }
      if (productFilter) {
        params.append('product_name', productFilter)
      }
      params.append('page', String(page))
      params.append('page_size', String(pageSize))
      params.append('sort', sort)

      if (params.toString()) {
        url += `?${params.toString()}`
      }

      const response = await fetch(url)
      const data = await response.json()
      
      if (data.success) {
        setReviews(data.reviews || [])
        setTotalPages(data.total_pages || 1)
      } else {
        setError(data.error || 'Gagal mengambil data ulasan')
      }
    } catch (error) {
      console.error('Error fetching reviews:', error)
      setError('Tidak dapat terhubung ke server')
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/reviews/stats`)
      const data = await response.json()
      if (data.success) {
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!productName.trim() || !reviewText.trim()) {
      setError('Mohon isi semua field')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze-review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_name: productName,
          review_text: reviewText,
        }),
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setSuccess(`✓ Ulasan berhasil dianalisis! Sentimen: ${data.sentiment} (${(data.confidence * 100).toFixed(1)}%)`)
        setProductName('')
        setReviewText('')
        fetchReviews()
        fetchStats()
      } else {
        setError(data.error || 'Gagal menganalisis ulasan')
      }
    } catch (error) {
      setError(`Error: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'POSITIVE':
        return '#22c55e'
      case 'NEGATIVE':
        return '#ef4444'
      case 'NEUTRAL':
        return '#f59e0b'
      default:
        return '#6b7280'
    }
  }

  const getSentimentLabel = (sentiment) => {
    switch (sentiment) {
      case 'POSITIVE':
        return 'Positif'
      case 'NEGATIVE':
        return 'Negatif'
      case 'NEUTRAL':
        return 'Netral'
      default:
        return sentiment
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🎯 Analisis Ulasan Produk</h1>
        <p>Analisis sentimen dengan Hugging Face • Ekstrak poin utama dengan Gemini AI</p>
      </header>

      <div className="container">
        {/* Error/Success Messages */}
        {error && (
          <div className="message error-message">
            ❌ {error}
            <button onClick={() => setError(null)} className="close-btn">×</button>
          </div>
        )}
        {success && (
          <div className="message success-message">
            {success}
            <button onClick={() => setSuccess(null)} className="close-btn">×</button>
          </div>
        )}

        {/* Input Section */}
        <section className="input-section">
          <h2>📝 Tambah Ulasan Baru</h2>
          <form onSubmit={handleSubmit} className="review-form">
            <div className="form-group">
              <label htmlFor="product">Nama Produk</label>
              <input
                id="product"
                type="text"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                placeholder="contoh: iPhone 15 Pro, Mouse Logitech"
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="review">Teks Ulasan</label>
              <textarea
                id="review"
                value={reviewText}
                onChange={(e) => setReviewText(e.target.value)}
                placeholder="Tulis ulasan produk Anda di sini... (dalam Bahasa Indonesia atau English)"
                rows="5"
                disabled={loading}
                required
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? '⏳ Menganalisis...' : '✨ Analisis Ulasan'}
            </button>
          </form>
        </section>

        {/* Stats Section */}
        {stats && stats.total > 0 && (
          <section className="stats-section">
            <h2>📊 Statistik Ulasan</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>{stats.total}</h3>
                <p>Total Ulasan</p>
              </div>
              <div className="stat-card positive">
                <h3>{stats.positive}</h3>
                <p>Positif ({stats.positive_percentage}%)</p>
              </div>
              <div className="stat-card negative">
                <h3>{stats.negative}</h3>
                <p>Negatif ({stats.negative_percentage}%)</p>
              </div>
              <div className="stat-card neutral">
                <h3>{stats.neutral}</h3>
                <p>Netral ({stats.neutral_percentage}%)</p>
              </div>
            </div>
          </section>
        )}

        {/* Filter Section */}
        <section className="filter-section">
          <div className="filter-header">
            <h2>🔍 Cari & Filter Ulasan</h2>
            {(productFilter || filter !== 'all') && (
              <button
                type="button"
                className="btn-reset-filters"
                onClick={() => { 
                  setProductFilter(''); 
                  setFilter('all'); 
                  setPage(1); 
                }}
              >
                🔄 Reset Semua Filter
              </button>
            )}
          </div>
          
          <div className="filters-container">
            {/* Search Box */}
            <div className="search-box">
              <div className="search-input-wrapper">
                <span className="search-icon">🔍</span>
                <input
                  id="product-filter"
                  type="text"
                  className="search-input"
                  value={productFilter}
                  onChange={(e) => { setProductFilter(e.target.value); setPage(1); }}
                  placeholder="Cari nama produk..."
                />
                {productFilter && (
                  <button
                    type="button"
                    className="clear-search-btn"
                    onClick={() => { setProductFilter(''); setPage(1); }}
                    title="Hapus pencarian"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>

            {/* Filter Options */}
            <div className="filters-grid">
              <div className="filter-group">
                <label htmlFor="sentiment-filter">
                  <span className="filter-icon">😊</span>
                  Filter Sentimen
                </label>
                <select 
                  id="sentiment-filter"
                  className="filter-select"
                  value={filter} 
                  onChange={(e) => { setFilter(e.target.value); setPage(1); }}
                >
                  <option value="all">✨ Semua Sentimen</option>
                  <option value="positive">😊 Positif</option>
                  <option value="negative">😞 Negatif</option>
                  <option value="neutral">😐 Netral</option>
                </select>
              </div>

              <div className="filter-group">
                <label htmlFor="sort">
                  <span className="filter-icon">📊</span>
                  Urutkan
                </label>
                <select
                  id="sort"
                  className="filter-select"
                  value={sort}
                  onChange={(e) => { setSort(e.target.value); setPage(1); }}
                >
                  <option value="created_at_desc">🆕 Terbaru</option>
                  <option value="created_at_asc">⏰ Terlama</option>
                  <option value="confidence_desc">⬆️ Keyakinan Tertinggi</option>
                  <option value="confidence_asc">⬇️ Keyakinan Terendah</option>
                </select>
              </div>

              <div className="filter-group">
                <label htmlFor="page-size">
                  <span className="filter-icon">📄</span>
                  Per Halaman
                </label>
                <select
                  id="page-size"
                  className="filter-select"
                  value={pageSize}
                  onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}
                >
                  <option value={5}>5 ulasan</option>
                  <option value={10}>10 ulasan</option>
                  <option value={20}>20 ulasan</option>
                  <option value={50}>50 ulasan</option>
                </select>
              </div>
            </div>
          </div>
        </section>

        {/* Reviews List */}
        <section className="reviews-section">
          <h2>📋 Daftar Ulasan ({reviews.length})</h2>
          {reviews.length === 0 ? (
            <p className="no-reviews">
              {productFilter || filter !== 'all' 
                ? 'Tidak ada ulasan yang cocok dengan filter Anda' 
                : 'Belum ada ulasan. Mulai dengan menganalisis ulasan pertama!'}
            </p>
          ) : (
            <>
              <div className="reviews-grid">
                {reviews.map((review) => (
                  <div key={review.id} className="review-card">
                    <div className="review-header">
                      <h3>{review.product_name}</h3>
                      <span 
                        className="sentiment-badge"
                        style={{ backgroundColor: getSentimentColor(review.sentiment) }}
                      >
                        {getSentimentLabel(review.sentiment)}
                      </span>
                    </div>
                    <p className="review-text">{review.review_text}</p>
                    
                    <div className="review-meta">
                      <span className="confidence">
                        Keyakinan: {(review.confidence * 100).toFixed(1)}%
                      </span>
                    </div>

                    {review.key_points && review.key_points.length > 0 && (
                      <div className="key-points">
                        <strong>🔑 Poin Utama:</strong>
                        <ul>
                          {review.key_points.map((point, idx) => (
                            <li key={idx}>{point}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <p className="review-date">
                      📅 {new Date(review.created_at).toLocaleString('id-ID')}
                    </p>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    className="btn btn-secondary"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page <= 1}
                  >
                    ← Sebelumnya
                  </button>
                  <span className="page-info">
                    Halaman {page} dari {totalPages}
                  </span>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page >= totalPages}
                  >
                    Berikutnya →
                  </button>
                </div>
              )}
            </>
          )}
        </section>
      </div>

      <footer className="footer">
        <p>Product Review Analyzer | Hugging Face Sentiment • Gemini Key Points</p>
      </footer>
    </div>
  )
}

export default App
