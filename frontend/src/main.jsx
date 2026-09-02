import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import './i18n'
import App from './App'
import './styles/index.css'

if (import.meta.env.VITE_API_BASE_URL) {
    axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL
}

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)
