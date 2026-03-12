import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { CircularProgress, Box } from '@mui/material';
import Layout from './components/Layout';
import PublicLayout from './components/PublicLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Members from './pages/Members';
import Events from './pages/Events';
import Memberships from './pages/Memberships';
import AdminDashboard from './pages/AdminDashboard';

// Public Pages
import Home from './pages/Home';
import About from './pages/About';
import PublicEvents from './pages/Events';
import Membership from './pages/Membership';
import Contact from './pages/Contact';

import { fetchCurrentUser } from './store/slices/authSlice';

// Protected Route Component
const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, loading, user } = useSelector((state) => state.auth);
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (requireAdmin) {
    const isAdmin = user?.is_superuser || 
      (user?.member_profile && (user.member_profile.block || user.member_profile.district || user.member_profile.state));
    if (!isAdmin) {
      return <Navigate to="/dashboard" />;
    }
  }
  
  return children;
};

// Auth Route (redirect if authenticated to dashboard)
const AuthRoute = ({ children }) => {
  const { isAuthenticated } = useSelector((state) => state.auth);
  return isAuthenticated ? <Navigate to="/dashboard" /> : children;
};

function App() {
  const dispatch = useDispatch();
  const { isAuthenticated, token } = useSelector((state) => state.auth);

  useEffect(() => {
    if (token && !isAuthenticated) {
      dispatch(fetchCurrentUser());
    }
  }, [dispatch, token, isAuthenticated]);

  return (
    <Routes>
      {/* ==================== PUBLIC ROUTES ==================== */}
      {/* These routes are accessible without authentication */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/events" element={<PublicEvents />} />
        <Route path="/membership" element={<Membership />} />
        <Route path="/contact" element={<Contact />} />
      </Route>

      {/* ==================== AUTH ROUTES ==================== */}
      {/* These routes redirect to dashboard if already authenticated */}
      <Route path="/login" element={<AuthRoute><Login /></AuthRoute>} />
      <Route path="/register" element={<AuthRoute><Register /></AuthRoute>} />
      <Route path="/forgot-password" element={<AuthRoute><ForgotPassword /></AuthRoute>} />
      
      {/* ==================== PROTECTED ROUTES ==================== */}
      {/* These routes require authentication */}
      <Route path="/app" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="members" element={<Members />} />
        <Route path="events" element={<Events />} />
        <Route path="memberships" element={<Memberships />} />
        <Route path="admin" element={
          <ProtectedRoute requireAdmin>
            <AdminDashboard />
          </ProtectedRoute>
        } />
      </Route>
      
      {/* Legacy route for dashboard - redirects to /app/dashboard */}
      <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
      
      {/* Catch all - redirect to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
