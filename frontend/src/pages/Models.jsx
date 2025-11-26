import React, { useEffect, useState } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  IconButton,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Card,
  CardContent,
  Grid
} from "@mui/material";
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Inventory as InventoryIcon,
  AddCircle as AddCircleIcon,
  Edit as EditInventoryIcon
} from "@mui/icons-material";
import { 
  listModels, 
  createModel, 
  updateModel, 
  deleteModel, 
  getInventory,
  updateInventory,
  getInventoryItem
} from "../services/api";

export default function Models() {
  const [models, setModels] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });
  const [dialogOpen, setDialogOpen] = useState(false);
  const [inventoryDialogOpen, setInventoryDialogOpen] = useState(false);
  const [editingModel, setEditingModel] = useState(null);
  const [editingInventory, setEditingInventory] = useState(null);
  const [form, setForm] = useState({
    sku: "",
    name: "",
    shipping_mode: "CKD F",
    status: "2025 Product",
    remarks: "",
    safety_stock_days: 45,
    safety_threshold_percentage: 20.0,
    lead_time_weeks: 10
  });
  const [inventoryForm, setInventoryForm] = useState({
    product_id: null,
    current_stock: 0,
    cbu_in_hand: 0,
    kits_in_factory: 0
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [modelsResponse, inventoryResponse] = await Promise.all([
        listModels(),
        getInventory()
      ]);
      setModels(modelsResponse.data);
      setInventory(inventoryResponse.data);
    } catch (error) {
      showSnackbar("Failed to load data", "error");
    } finally {
      setLoading(false);
    }
  };

  const showSnackbar = (message, severity = "success") => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const resetForm = () => {
    setForm({
      sku: "",
      name: "",
      shipping_mode: "CKD F",
      status: "2025 Product",
      remarks: "",
      safety_stock_days: 45,
      safety_threshold_percentage: 20.0,
      lead_time_weeks: 10
    });
    setEditingModel(null);
  };

  const resetInventoryForm = () => {
    setInventoryForm({
      product_id: null,
      current_stock: 0,
      cbu_in_hand: 0,
      kits_in_factory: 0
    });
    setEditingInventory(null);
  };

  const handleSubmit = async () => {
    if (!form.sku || !form.name) {
      showSnackbar("SKU and Name are required", "error");
      return;
    }

    // Validate numeric fields
    if (form.safety_stock_days < 0) {
      showSnackbar("Safety Stock Days must be 0 or greater", "error");
      return;
    }
    if (form.safety_threshold_percentage < 0 || form.safety_threshold_percentage > 100) {
      showSnackbar("Safety Threshold must be between 0 and 100", "error");
      return;
    }
    if (form.lead_time_weeks < 1) {
      showSnackbar("Lead Time must be at least 1 week", "error");
      return;
    }

    try {
      // Prepare payload - convert empty strings to null for optional fields
      const payload = {
        ...form,
        remarks: form.remarks.trim() || null,  // Convert empty string to null
        safety_stock_days: parseInt(form.safety_stock_days) || 45,
        safety_threshold_percentage: parseFloat(form.safety_threshold_percentage) || 20.0,
        lead_time_weeks: parseInt(form.lead_time_weeks) || 10
      };

      if (editingModel) {
        await updateModel(editingModel.id, payload);
        showSnackbar("Model updated successfully");
      } else {
        await createModel(payload);
        showSnackbar("Model created successfully");
      }
      setDialogOpen(false);
      resetForm();
      loadData();
    } catch (error) {
      console.error("Model operation error:", error);
      const errorMessage = error.response?.data?.detail || error.message || "Operation failed";
      showSnackbar(errorMessage, "error");
    }
  };

  const handleEdit = (model) => {
    setEditingModel(model);
    setForm({
      sku: model.sku,
      name: model.name,
      shipping_mode: model.shipping_mode,
      status: model.status,
      remarks: model.remarks || "",
      safety_stock_days: model.safety_stock_days || 45,
      safety_threshold_percentage: model.safety_threshold_percentage || 20.0,
      lead_time_weeks: model.lead_time_weeks || 10
    });
    setDialogOpen(true);
  };

  const handleEditInventory = async (model) => {
    try {
      // Get current inventory for this product
      const invResponse = await getInventoryItem(model.id);
      const invData = invResponse.data;
      
      setEditingInventory(model);
      setInventoryForm({
        product_id: model.id,
        current_stock: invData.current_stock || 0,
        cbu_in_hand: invData.cbu_in_hand || 0,
        kits_in_factory: invData.kits_in_factory || 0
      });
      setInventoryDialogOpen(true);
    } catch (error) {
      // If inventory doesn't exist, create new form
      setEditingInventory(model);
      setInventoryForm({
        product_id: model.id,
        current_stock: 0,
        cbu_in_hand: 0,
        kits_in_factory: 0
      });
      setInventoryDialogOpen(true);
    }
  };

  const handleInventorySubmit = async () => {
    try {
      await updateInventory(inventoryForm);
      showSnackbar("Inventory updated successfully");
      setInventoryDialogOpen(false);
      resetInventoryForm();
      loadData();
    } catch (error) {
      showSnackbar(error.response?.data?.detail || "Failed to update inventory", "error");
    }
  };

  const handleDelete = async (modelId, modelName) => {
    if (!window.confirm(`Are you sure you want to delete "${modelName}"?`)) return;
    
    try {
      await deleteModel(modelId);
      showSnackbar("Model deleted successfully");
      loadData();
    } catch (error) {
      showSnackbar(error.response?.data?.detail || "Delete failed", "error");
    }
  };

  const getModelInventory = (modelId) => {
    return inventory.find(item => item.product_id === modelId) || { current_stock: 0 };
  };

  const getStockStatus = (model) => {
    const modelInventory = getModelInventory(model.id);
    const currentStock = modelInventory.current_stock || 0;
    const safetyThreshold = model.safety_threshold_percentage || 20.0;
    const safetyStock = Math.round(currentStock * (safetyThreshold / 100.0));
    
    if (currentStock === 0) return { status: "Out of Stock", color: "error" };
    if (currentStock <= safetyStock) return { status: "Critical", color: "error" };
    if (currentStock <= safetyStock * 1.2) return { status: "Warning", color: "warning" };
    return { status: "Safe", color: "success" };
  };

  // Statistics
  const stats = {
    totalModels: models.length,
    activeModels: models.filter(m => m.is_active).length,
    lowStockModels: models.filter(model => {
      const inventory = getModelInventory(model.id);
      const currentStock = inventory.current_stock || 0;
      const safetyThreshold = model.safety_threshold_percentage || 20.0;
      const safetyStock = Math.round(currentStock * (safetyThreshold / 100.0));
      return currentStock <= safetyStock;
    }).length,
    newProducts: models.filter(m => m.status.includes('2026')).length
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Product Models Management
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="overline">
                Total Models
              </Typography>
              <Typography variant="h4">{stats.totalModels}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="overline">
                Active Models
              </Typography>
              <Typography variant="h4">{stats.activeModels}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="overline">
                Low Stock
              </Typography>
              <Typography variant="h4" color="warning.main">
                {stats.lowStockModels}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="overline">
                2026 Products
              </Typography>
              <Typography variant="h4" color="info.main">
                {stats.newProducts}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Bar */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">
          Product Models ({models.length})
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={() => { resetForm(); setDialogOpen(true); }}
        >
          Add New Model
        </Button>
      </Box>

      {/* Models Table */}
      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>SKU</strong></TableCell>
              <TableCell><strong>Name</strong></TableCell>
              <TableCell><strong>Shipping Mode</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Current Stock</strong></TableCell>
              <TableCell><strong>Safety Stock Days</strong></TableCell>
              <TableCell><strong>Stock Status</strong></TableCell>
              <TableCell><strong>Remarks</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {models.map((model) => {
              const modelInventory = getModelInventory(model.id);
              const stockStatus = getStockStatus(model);
              
              return (
                <TableRow key={model.id} hover>
                  <TableCell sx={{ fontFamily: 'monospace', fontWeight: 'bold' }}>
                    {model.sku}
                  </TableCell>
                  <TableCell>{model.name}</TableCell>
                  <TableCell>
                    <Chip label={model.shipping_mode} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={model.status} 
                      color={model.status.includes('2026') ? 'info' : 'primary'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <InventoryIcon fontSize="small" color="action" />
                      <Typography fontWeight="medium">
                        {modelInventory.current_stock || 0}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {model.safety_stock_days} days
                    </Typography>
                    <Typography variant="caption" color="textSecondary" display="block">
                      Threshold: {model.safety_threshold_percentage || 20}% | Lead: {model.lead_time_weeks || 10}w
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={stockStatus.status} 
                      color={stockStatus.color}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="textSecondary">
                      {model.remarks || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <IconButton 
                        color="success" 
                        size="small"
                        onClick={() => handleEditInventory(model)}
                        title="Manage Inventory"
                      >
                        <InventoryIcon />
                      </IconButton>
                      <IconButton color="primary" size="small" onClick={() => handleEdit(model)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        color="error" 
                        size="small"
                        onClick={() => handleDelete(model.id, model.name)}
                        disabled={!model.is_active}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>

        {models.length === 0 && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography color="textSecondary">
              No product models found. Create your first model to get started.
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingModel ? 'Edit Product Model' : 'Add New Product Model'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="SKU"
              value={form.sku}
              onChange={(e) => setForm({ ...form, sku: e.target.value })}
              required
              helperText="Unique product identifier"
            />
            <TextField
              label="Name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
            <FormControl fullWidth>
              <InputLabel>Shipping Mode</InputLabel>
              <Select
                value={form.shipping_mode}
                label="Shipping Mode"
                onChange={(e) => setForm({ ...form, shipping_mode: e.target.value })}
              >
                <MenuItem value="CKD F">CKD F</MenuItem>
                <MenuItem value="CBU">CBU</MenuItem>
                <MenuItem value="SKD">SKD</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={form.status}
                label="Status"
                onChange={(e) => setForm({ ...form, status: e.target.value })}
              >
                <MenuItem value="2025 Product">2025 Product</MenuItem>
                <MenuItem value="2026 New Product">2026 New Product</MenuItem>
                <MenuItem value="Discontinued">Discontinued</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Safety Stock Days"
              type="number"
              value={form.safety_stock_days}
              onChange={(e) => setForm({ ...form, safety_stock_days: parseInt(e.target.value) || 0 })}
              helperText="Target days of supply for inventory management"
            />
            <TextField
              label="Safety Threshold (%)"
              type="number"
              value={form.safety_threshold_percentage}
              onChange={(e) => setForm({ ...form, safety_threshold_percentage: parseFloat(e.target.value) || 20.0 })}
              helperText="Safety stock as percentage of current inventory (default: 20%)"
              inputProps={{ min: 0, max: 100, step: 0.1 }}
            />
            <TextField
              label="Lead Time (weeks)"
              type="number"
              value={form.lead_time_weeks}
              onChange={(e) => setForm({ ...form, lead_time_weeks: parseInt(e.target.value) || 10 })}
              helperText="Lead time in weeks for purchase orders (default: 10 weeks)"
              inputProps={{ min: 1 }}
            />
            <TextField
              label="Remarks"
              multiline
              rows={2}
              value={form.remarks}
              onChange={(e) => setForm({ ...form, remarks: e.target.value })}
              helperText="Additional notes or comments"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingModel ? 'Update Model' : 'Create Model'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Inventory Management Dialog */}
      <Dialog open={inventoryDialogOpen} onClose={() => setInventoryDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <InventoryIcon />
            Manage Inventory - {editingInventory?.sku} {editingInventory?.name}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Update inventory quantities for this product. Sales will automatically reduce current stock.
            </Alert>
            <TextField
              label="Current Stock"
              type="number"
              value={inventoryForm.current_stock}
              onChange={(e) => setInventoryForm({ ...inventoryForm, current_stock: parseInt(e.target.value) || 0 })}
              helperText="Available inventory for sales"
              inputProps={{ min: 0 }}
              fullWidth
            />
            <TextField
              label="CBU in Hand"
              type="number"
              value={inventoryForm.cbu_in_hand}
              onChange={(e) => setInventoryForm({ ...inventoryForm, cbu_in_hand: parseInt(e.target.value) || 0 })}
              helperText="Complete Built Units in warehouse"
              inputProps={{ min: 0 }}
              fullWidth
            />
            <TextField
              label="Kits in Factory"
              type="number"
              value={inventoryForm.kits_in_factory}
              onChange={(e) => setInventoryForm({ ...inventoryForm, kits_in_factory: parseInt(e.target.value) || 0 })}
              helperText="CKD kits being assembled in factory"
              inputProps={{ min: 0 }}
              fullWidth
            />
            {editingInventory && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Product Configuration
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Safety Threshold: {editingInventory.safety_threshold_percentage || 20}%
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Lead Time: {editingInventory.lead_time_weeks || 10} weeks
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Safety Stock: {Math.round((inventoryForm.current_stock || 0) * ((editingInventory.safety_threshold_percentage || 20) / 100))} units
                </Typography>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setInventoryDialogOpen(false); resetInventoryForm(); }}>
            Cancel
          </Button>
          <Button onClick={handleInventorySubmit} variant="contained" color="primary">
            Update Inventory
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={4000} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}