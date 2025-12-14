# Product Review Analyzer

Aplikasi analisis ulasan produk dengan AI menggunakan:
- **Hugging Face** untuk sentiment analysis (positive/negative/neutral)
- **Gemini AI** untuk ekstraksi key points
- **PostgreSQL** untuk penyimpanan data
- **Pyramid** (Python) untuk backend API
- **React + Vite** untuk frontend

## Fitur

Analisis sentimen ulasan dengan Hugging Face  
Ekstraksi poin-poin utama dengan Gemini AI  
Pencarian ulasan berdasarkan nama produk  
Filter berdasarkan sentimen (positive/negative/neutral)  
Error handling dan loading states  

## Setup

### 1. Backend (Pyramid + PostgreSQL)

```powershell
# Masuk ke folder backend
cd "BackEnd\BackEnd"

# Install dependencies
pip install -e .

# Setup database (akan menanyakan credentials PostgreSQL Anda)
python setup_database.py

# Update development.ini dengan connection string yang diberikan

# Jalankan server
pserve development.ini
```

Backend akan berjalan di: `http://localhost:6543`

### 2. Frontend (React + Vite)

```powershell
# Masuk ke folder frontend
cd FrontEnd

# Install dependencies
npm install

# Jalankan dev server
npm run dev
```

Frontend akan berjalan di: `http://localhost:5173`

## API Endpoints

### POST /api/analyze-review
Analisis ulasan baru
```json
{
  "product_name": "iPhone 15 Pro",
  "review_text": "Produk bagus, kamera luar biasa!"
}
```

Response:
```json
{
  "success": true,
  "id": 1,
  "product_name": "iPhone 15 Pro",
  "review_text": "Produk bagus, kamera luar biasa!",
  "sentiment": "POSITIVE",
  "confidence": 0.95,
  "key_points": ["Kualitas bagus", "Kamera excellent"],
  "created_at": "2025-12-11T10:30:00"
}
## Struktur Project

```
123140197_tugas3/
├── BackEnd/
│   └── BackEnd/
│       ├── BackEnd/
│       │   ├── models/
│       │   │   ├── __init__.py
│       │   │   ├── meta.py
│       │   │   └── review.py
│       │   ├── views/
│       │   │   └── __init__.py
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── development.ini
│       ├── setup.py
│       └── setup_database.py
└── FrontEnd/
    ├── src/
    │   ├── App.jsx
    │   ├── App.css
    │   ├── main.jsx
    │   └── index.css
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## Technologies Used

- **Backend**: Python 3.x, Pyramid, SQLAlchemy, psycopg2
- **AI**: Hugging Face API, Google Gemini API
- **Database**: PostgreSQL
- **Frontend**: React 18, Vite
- **Styling**: CSS3 dengan gradients dan animations


Tugas 3 - PEMWEB - 123140197
