
import React from 'react';
import { BrowserRouter as Router, NavLink, Navigate, Outlet, Routes, Route } from 'react-router-dom';
import './App.css';
import { clearSession, getAuthSession } from './utils/auth';

import LandingPage from './pages/LandingPage';
import AuthPage from './pages/AuthPage';
import ItemUpload from './pages/ItemUpload';
import Dashboard from './pages/Dashboard';
import ExpertDirectory from './pages/ExpertDirectory';
import SuggestionsPage from './pages/SuggestionsPage';
import AdminPanel from './pages/AdminPanel';
import EcoTipsPage from './pages/EcoTipsPage';
import ConnectionRequestsPage from './pages/ConnectionRequestsPage';
import MyItemsPage from './pages/MyItemsPage';

const ProtectedRoute = () => {
  const { isAuthenticated } = getAuthSession();
  return isAuthenticated ? <Outlet /> : <Navigate to="/auth" replace />;
};

const AdminRoute = () => {
  const { isAuthenticated, role } = getAuthSession();
  if (!isAuthenticated) return <Navigate to="/auth" replace />;
  return role === 'ADMIN' ? <Outlet /> : <Navigate to="/dashboard" replace />;
};

function App() {
  const { isAuthenticated, role } = getAuthSession();

  const navItems = !isAuthenticated
    ? [
      { to: '/', label: 'Home' },
      { to: '/auth', label: 'Sign In' },
    ]
    : role === 'USER'
      ? [
        { to: '/dashboard', label: 'Dashboard' },
        { to: '/upload', label: 'Upload Item' },
        { to: '/my-items', label: 'My Items' },
        { to: '/experts', label: 'Experts' },
        { to: '/eco-tips', label: 'EcoTips' },
        { to: '/connection-requests', label: 'My Requests' },
      ]
      : role === 'EXPERT'
        ? [
          { to: '/dashboard', label: 'Dashboard' },
          { to: '/connection-requests', label: 'Connection Requests' },
          { to: '/experts', label: 'Experts' },
          { to: '/eco-tips', label: 'EcoTips' },
        ]
        : [
          { to: '/dashboard', label: 'Dashboard' },
          { to: '/admin', label: 'Admin Dashboard' },
          { to: '/connection-requests', label: 'Connection Requests' },
          { to: '/experts', label: 'Experts' },
          { to: '/eco-tips', label: 'EcoTips' },
        ];

  return (
    <Router>
      <div className="app-shell">
        <header className="topbar">
          <div className="brand-block">
            <h1 className="brand">Panolive</h1>
          </div>

          <nav className="top-nav" aria-label="Primary navigation">
            {navItems.map((item) => (
              <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                {item.label}
              </NavLink>
            ))}
            {isAuthenticated && (
              <button
                className="nav-link nav-btn"
                onClick={() => {
                  clearSession();
                  window.location.href = '/';
                }}
              >
                Sign Out
              </button>
            )}
          </nav>
        </header>

        <main className="page-wrap">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/auth" element={<AuthPage />} />

            <Route element={<ProtectedRoute />}>
              <Route path="/upload" element={<ItemUpload />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/my-items" element={<MyItemsPage />} />
              <Route path="/suggestions" element={<SuggestionsPage />} />
              <Route path="/experts" element={<ExpertDirectory />} />
              <Route path="/eco-tips" element={<EcoTipsPage />} />
              <Route path="/connection-requests" element={<ConnectionRequestsPage />} />
            </Route>

            <Route element={<AdminRoute />}>
              <Route path="/admin" element={<AdminPanel />} />
            </Route>

            <Route path="*" element={<Navigate to={isAuthenticated ? '/dashboard' : '/'} replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
