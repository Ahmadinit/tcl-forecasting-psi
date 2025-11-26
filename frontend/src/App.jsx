import React, { useState, useEffect } from 'react';
import {
  Box,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Typography
} from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

// Pages
import Dashboard from './pages/Dashboard';
import Models from './pages/Models';
import Inventory from './pages/Inventory';
import Sales from './pages/Sales';
import PurchaseOrders from './pages/PurchaseOrders';
import Shipments from './pages/Shipments';
import Settings from './pages/Settings';
import Login from './pages/Login';

// Services
import { checkAuthSetup, getUser } from './services/api';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  // Check localStorage for existing auth state
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('isAuthenticated') === 'true';
  });
  const [mobileOpen, setMobileOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    // If already authenticated from localStorage, verify with backend
    if (isAuthenticated) {
      try {
        const setupResponse = await checkAuthSetup();
        if (setupResponse?.data?.is_setup) {
          setLoading(false);
          return; // Already authenticated, no need to change state
        } else {
          // Backend says not set up, clear auth
          setIsAuthenticated(false);
          localStorage.removeItem('isAuthenticated');
        }
      } catch (error) {
        // If backend is down but we have localStorage auth, keep authenticated
        // This allows the app to work even if backend temporarily goes down
        if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
          // Keep authenticated state from localStorage
          setLoading(false);
          return;
        }
        // Other errors - clear auth
        setIsAuthenticated(false);
        localStorage.removeItem('isAuthenticated');
      }
    } else {
      // Not authenticated, check if backend is set up
      try {
        const setupResponse = await checkAuthSetup();
        if (setupResponse?.data?.is_setup) {
          // Backend is set up, but user not logged in - show login
          setIsAuthenticated(false);
        } else {
          // Backend not set up - show login to create first user
          setIsAuthenticated(false);
        }
      } catch (error) {
        // Backend error - show login
        setIsAuthenticated(false);
      }
    }
    setLoading(false);
  };

  const handleLogin = () => {
    setIsAuthenticated(true);
    localStorage.setItem('isAuthenticated', 'true');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('isAuthenticated');
  };

  const handleMobileClose = () => {
    setMobileOpen(false);
  };

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          <Typography>Loading...</Typography>
        </Box>
      </ThemeProvider>
    );
  }

  if (!isAuthenticated) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Login onLogin={handleLogin} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
          <Navbar onLogout={handleLogout} />
          <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden', marginTop: '64px' }}>
            <Sidebar
              mobileOpen={mobileOpen}
              onMobileClose={handleMobileClose}
            />
            
            <Box 
              component="main" 
              sx={{ 
                flexGrow: 1,
                flexBasis: 0, // Allows flex item to shrink below content size
                p: 3, 
                overflow: 'auto',
                minWidth: 0, // Prevents flex item from overflowing
                backgroundColor: 'background.default'
              }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/models" element={<Models />} />
                <Route path="/inventory" element={<Inventory />} />
                <Route path="/sales" element={<Sales />} />
                <Route path="/purchase" element={<PurchaseOrders />} />
                <Route path="/shipments" element={<Shipments />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Box>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;