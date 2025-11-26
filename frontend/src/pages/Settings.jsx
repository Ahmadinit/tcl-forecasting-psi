// frontend/src/pages/Settings.jsx
import React, { useEffect, useState } from "react";
import { 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Button,
  Grid,
  Divider,
  Alert,
  Switch,
  FormControlLabel
} from "@mui/material";
import { getSettings, bulkUpdateSettings } from "../services/api";

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [form, setForm] = useState({
    default_safety_threshold: 20.0,
    default_lead_time_weeks: 10,
    business_days: 5,
    financial_year_start: "2025-01-01",
    low_stock_alerts_enabled: true,
    auto_po_suggestions_enabled: true
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const res = await getSettings();
      const settingsDict = {};
      if (Array.isArray(res.data)) {
        res.data.forEach(s => {
          settingsDict[s.config_key] = s.config_value;
        });
      }
      
      setSettings(res.data);
      setForm({
        default_safety_threshold: parseFloat(settingsDict.default_safety_threshold || 20.0),
        default_lead_time_weeks: parseInt(settingsDict.default_lead_time_weeks || 10),
        business_days: parseInt(settingsDict.business_days || 5),
        financial_year_start: settingsDict.financial_year_start || "2025-01-01",
        low_stock_alerts_enabled: settingsDict.low_stock_alerts_enabled === 'true' || settingsDict.low_stock_alerts_enabled === true,
        auto_po_suggestions_enabled: settingsDict.auto_po_suggestions_enabled === 'true' || settingsDict.auto_po_suggestions_enabled === true
      });
    } catch (err) {
      console.error("Failed to load settings:", err);
    }
  };

  const submit = async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });
    
    try {
      const settingsToUpdate = {
        default_safety_threshold: form.default_safety_threshold.toString(),
        default_lead_time_weeks: form.default_lead_time_weeks.toString(),
        business_days: form.business_days.toString(),
        financial_year_start: form.financial_year_start,
        low_stock_alerts_enabled: form.low_stock_alerts_enabled.toString(),
        auto_po_suggestions_enabled: form.auto_po_suggestions_enabled.toString()
      };
      
      await bulkUpdateSettings(settingsToUpdate);
      setMessage({ type: 'success', text: 'Settings saved successfully! They will persist after app restart.' });
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to update settings' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" mb={3}>System Settings</Typography>

      {message.text && (
        <Alert severity={message.type === 'success' ? 'success' : 'error'} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>System-Wide Configuration</Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          These settings apply system-wide and persist after app restart. Click "Update Settings" to save.
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              label="Default Safety Threshold (%)"
              type="number"
              fullWidth
              value={form.default_safety_threshold ?? 20.0}
              onChange={(e) => setForm({ ...form, default_safety_threshold: parseFloat(e.target.value) || 20.0 })}
              helperText="Default safety stock as percentage of current inventory (default: 20%)"
              inputProps={{ min: 0, max: 100, step: 0.1 }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label="Default Lead Time (weeks)"
              type="number"
              fullWidth
              value={form.default_lead_time_weeks ?? 10}
              onChange={(e) => setForm({ ...form, default_lead_time_weeks: parseInt(e.target.value) || 10 })}
              helperText="Default lead time in weeks for new products (default: 10 weeks)"
              inputProps={{ min: 1 }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label="Business Days per Week"
              type="number"
              fullWidth
              value={form.business_days ?? 5}
              onChange={(e) => setForm({ ...form, business_days: parseInt(e.target.value) || 5 })}
              helperText="Number of business days per week (default: 5, Monday-Friday)"
              inputProps={{ min: 1, max: 7 }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label="Financial Year Start Date"
              type="date"
              fullWidth
              value={form.financial_year_start ?? "2025-01-01"}
              onChange={(e) => setForm({ ...form, financial_year_start: e.target.value })}
              helperText="Start date of financial year for week number calculations"
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={form.low_stock_alerts_enabled ?? true}
                  onChange={(e) => setForm({ ...form, low_stock_alerts_enabled: e.target.checked })}
                />
              }
              label="Enable Low Stock Alerts"
            />
            <Typography variant="caption" display="block" color="textSecondary">
              Show alerts on dashboard when inventory falls below safety stock
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={form.auto_po_suggestions_enabled ?? true}
                  onChange={(e) => setForm({ ...form, auto_po_suggestions_enabled: e.target.checked })}
                />
              }
              label="Enable Automatic PO Suggestions"
            />
            <Typography variant="caption" display="block" color="textSecondary">
              Automatically generate PO suggestions every week (Saturday)
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 3 }}>
              <Button variant="outlined" onClick={loadSettings}>
                Reset
              </Button>
              <Button 
                variant="contained" 
                onClick={submit}
                disabled={loading}
              >
                {loading ? 'Saving...' : 'Update Settings'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}
