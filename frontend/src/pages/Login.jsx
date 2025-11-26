// frontend/src/pages/Login.jsx
/* import React, { useState } from "react";
import { Box, Paper, Typography, TextField, Button } from "@mui/material";
import { authLogin, authCreate } from "../services/api";

export default function Login() {
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");

  const handleLogin = async () => {
    try {
      const res = await authLogin(form);
      // backend returns {message:...} — we store a dummy token for now
      localStorage.setItem("token", "local-token");
      window.location.href = "/dashboard";
    } catch (err) {
      setError(err?.response?.data?.detail || "Login failed");
    }
  };

  // helper to create a default user if none exists
  const handleCreate = async () => {
    try {
      await authCreate(form.username, form.password);
      setError("User created. Now click Login.");
    } catch (err) {
      setError(err?.response?.data?.detail || "Create failed");
    }
  };

  return (
    <Box
      sx={{
        display: "flex",
        height: "100vh",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Paper sx={{ p: 4, width: 380 }}>
        <Typography variant="h5" mb={2}>
          PSI Login
        </Typography>

        <TextField
          label="Username"
          fullWidth
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          sx={{ mb: 2 }}
        />
        <TextField
          label="Password"
          type="password"
          fullWidth
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          sx={{ mb: 2 }}
        />

        {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}

        <Box sx={{ display: "flex", gap: 2 }}>
          <Button variant="contained" onClick={handleLogin} fullWidth>
            Login
          </Button>
          <Button variant="outlined" onClick={handleCreate} fullWidth>
            Create
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}
*/


import React, { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Container
} from "@mui/material";
import { Inventory as InventoryIcon } from "@mui/icons-material";
import { authLogin, authCreate, checkAuthSetup } from "../services/api";

export default function Login({ onLogin }) {
  const [isSetup, setIsSetup] = useState(false);
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    checkSetup();
  }, []);

  const checkSetup = async () => {
    try {
      const response = await checkAuthSetup();
      setIsSetup(response?.data?.is_setup || false);
    } catch (error) {
      // Suppress error logging if backend is not running (expected in development)
      if (error.code !== 'ECONNREFUSED' && !error.message?.includes('Network Error')) {
        console.error("Failed to check setup:", error);
      }
      // If backend is not available, assume not set up
      setIsSetup(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (!isSetup) {
        // Create first user
        await authCreate(form.username, form.password);
        setIsSetup(true);
      }
      
      // Login
      const response = await authLogin(form);
      onLogin(); // This will set localStorage in App.jsx
    } catch (error) {
      setError(error.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <InventoryIcon sx={{ fontSize: 48, mb: 2, color: "primary.main" }} />
        <Typography component="h1" variant="h4" gutterBottom>
          PSI Forecast System
        </Typography>
        <Typography variant="subtitle1" color="textSecondary" gutterBottom>
          {isSetup ? "Sign in to your account" : "Create administrator account"}
        </Typography>

        <Paper elevation={3} sx={{ mt: 3, p: 4, width: "100%" }}>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              label="Username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              autoFocus
            />
            <TextField
              margin="normal"
              required
              fullWidth
              label="Password"
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {isSetup ? "Sign In" : "Create Account"}
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}