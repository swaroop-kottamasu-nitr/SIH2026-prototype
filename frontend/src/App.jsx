import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import i18n from './i18n'
import Landing from './pages/Landing'
import About from './pages/About'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import SoilAnalysis from './pages/SoilAnalysis'
import CropRecommendation from './pages/CropRecommendation'
import Weather from './pages/Weather'
import DiseaseDetection from './pages/DiseaseDetection'
import SoilTypeDetection from './pages/SoilTypeDetection'
import MarketPrices from './pages/MarketPrices'
import Irrigation from './pages/Irrigation'
import CropRotation from './pages/CropRotation'
import InputLocator from './pages/InputLocator'
import StorageLocator from './pages/StorageLocator'
import LabourBooking from './pages/LabourBooking'
import GovernmentSchemes from './pages/GovernmentSchemes'
import Chatbot from './pages/Chatbot'
import AlertDetail from './pages/AlertDetail'
import AlertBanner from './components/AlertBanner'

function App() {
    const [user, setUser] = useState(null)

    // Load user from localStorage on mount, sync i18n language
    useEffect(() => {
        const savedUser = localStorage.getItem('user')
        if (savedUser) {
            const u = JSON.parse(savedUser)
            setUser(u)
            if (u?.language) i18n.changeLanguage(u.language)
        } else {
            i18n.changeLanguage(i18n.options.lng || 'en')
        }
    }, [])

    const handleLogin = (userData) => {
        setUser(userData)
        localStorage.setItem('user', JSON.stringify(userData))
        const lang = userData?.language || 'en'
        i18n.changeLanguage(lang)
    }

    const handleLogout = () => {
        setUser(null)
        localStorage.removeItem('user')
    }

    return (
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
            {/* Global Alert Banner - shows on all authenticated pages */}
            {user && <AlertBanner user={user} />}

            <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/about" element={<About />} />
                <Route path="/login" element={<Login onLogin={handleLogin} />} />
                <Route path="/register" element={<Register />} />

                {/* Protected routes */}
                <Route
                    path="/dashboard"
                    element={user ? <Dashboard user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/soil-analysis"
                    element={user ? <SoilAnalysis user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/soil"
                    element={user ? <SoilAnalysis user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/soil-analysis"
                    element={user ? <SoilAnalysis user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/crop-recommendation"
                    element={user ? <CropRecommendation user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/crop-recommend"
                    element={user ? <CropRecommendation user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/crop-recommendation"
                    element={user ? <CropRecommendation user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/weather"
                    element={user ? <Weather user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/weather"
                    element={user ? <Weather user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/disease-detection"
                    element={user ? <DiseaseDetection user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/disease"
                    element={user ? <DiseaseDetection user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/disease-detection"
                    element={user ? <DiseaseDetection user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/soil-detection"
                    element={user ? <SoilTypeDetection user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/soil-detection"
                    element={user ? <SoilTypeDetection user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/market-prices"
                    element={user ? <MarketPrices user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/market"
                    element={user ? <MarketPrices user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/market-prices"
                    element={user ? <MarketPrices user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/irrigation"
                    element={user ? <Irrigation user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/irrigation"
                    element={user ? <Irrigation user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/crop-rotation"
                    element={user ? <CropRotation user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/crop-rotation"
                    element={user ? <CropRotation user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/inputs"
                    element={user ? <InputLocator user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/inputs"
                    element={user ? <InputLocator user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/storage"
                    element={user ? <StorageLocator user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/storage"
                    element={user ? <StorageLocator user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/labour"
                    element={user ? <LabourBooking user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/labour"
                    element={user ? <LabourBooking user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/schemes"
                    element={user ? <GovernmentSchemes user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/schemes"
                    element={user ? <GovernmentSchemes user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/chatbot"
                    element={user ? <Chatbot user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route
                    path="/dashboard/chatbot"
                    element={user ? <Chatbot user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />}
                />
                <Route path="/alert/:id" element={user ? <AlertDetail user={user} onLogout={handleLogout} onUserUpdate={handleLogin} /> : <Navigate to="/login" />} />
            </Routes>
        </Router>
    )
}

export default App
