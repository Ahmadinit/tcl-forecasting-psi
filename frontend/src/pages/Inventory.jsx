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
  Remove as RemoveIcon,
  Warning as WarningIcon
} from "@mui/icons-material";
import { 
  getInventory, 
  updateInventory, 
  subtractInventory, 
  deleteInventoryRecord,
  listModels,
  getLowStockAlerts 
} from "../services/api";

export default function Inventory() {
  const [inventory, setInventory] = useState([]);
  const [models, setModels] = useState([]);
  const [lowStockAlerts, setLowStockAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });
  const [updateDialogOpen, setUpdateDialogOpen] = useState(false);
  const [subtractDialogOpen, setSubtractDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [updateForm, setUpdateForm] = useState({ quantity: 0, cbu_in_hand: 0, kits_in_factory: 0 });
  const [subtractForm, setSubtractForm] = useState({ quantity: 0 });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [inventoryResponse, modelsResponse, alertsResponse] = await Promise.all([
        getInventory(),
        listModels(),
        getLowStockAlerts()
      ]);
      setInventory(inventoryResponse.data);
      setModels(modelsResponse.data);
      setLowStockAlerts(alertsResponse.data);
    } catch (error) {
      showSnackbar("Failed to load inventory data", "error");
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

  const handleUpdateInventory = async () => {
    if (!selectedProduct) return;

    try {
      await updateInventory({
        product_id: selectedProduct.product_id,
        current_stock: updateForm.quantity,
        cbu_in_hand: updateForm.cbu_in_hand,
        kits_in_factory: updateForm.kits_in_factory
      });
      showSnackbar("Inventory updated successfully");
      setUpdateDialogOpen(false);
      resetForms();
      loadData();
    } catch (error) {
      showSnackbar(error.response?.data?.detail || "Update failed", "error");
    }
  };

  const handleSubtractInventory = async () => {
    if (!selectedProduct) return;

    try {
      await subtractInventory({
        product_id: selectedProduct.product_id,
        quantity: subtractForm.quantity
      });
      showSnackbar("Inventory subtracted successfully");
      setSubtractDialogOpen(false);
      resetForms();
      loadData();
    } catch (error) {
      showSnackbar(error.response?.data?.detail || "Subtraction failed", "error");
    }
  };

  const handleDelete = async (productId, productName) => {
    if (!window.confirm(`Are you sure you want to delete inventory for "${productName}"?`)) return;
    
    try {
      await deleteInventoryRecord(productId);
      showSnackbar("Inventory record deleted successfully");
      loadData();
    } catch (error) {
      showSnackbar(error.response?.data?.detail || "Delete failed", "error");
    }
  };

  const resetForms = () => {
    setUpdateForm({ quantity: 0, cbu_in_hand: 0, kits_in_factory: 0 });
    setSubtractForm({ quantity: 0 });
    setSelectedProduct(null);
  };

  const openUpdateDialog = (product) => {
    setSelectedProduct(product);
    setUpdateForm({
      quantity: product.current_stock,
      cbu_in_hand: product.cbu_in_hand,
      kits_in_factory: product.kits_in_factory
    });
    setUpdateDialogOpen(true);
  };

  const openSubtractDialog = (product) => {
    setSelectedProduct(product);
    setSubtractForm({ quantity: 0 });
    setSubtractDialogOpen(true);
  };

  // Statistics
  const stats = {
    totalItems: inventory.length,
    totalStock: inventory.reduce((sum, item) => sum + item.current_stock, 0),
    lowStockItems: lowStockAlerts.length,
    outOfStock: inventory.filter(item => item.current_stock === 0).length
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Inventory Management
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="overline">
                Total Items
              </Typography>
              <Typography variant="h4">{stats.totalItems}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="overline">
                Total Stock
              </Typography>
              <Typography variant="h4">{stats.totalStock.toLocaleString()}</Typography>
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
                {stats.lowStockItems}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="overline">
                Out of Stock
              </Typography>
              <Typography variant="h4" color="error.main">
                {stats.outOfStock}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Low Stock Alerts */}
      {lowStockAlerts.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <WarningIcon sx={{ mr: 1 }} />
          {lowStockAlerts.length} product(s) have low stock levels
        </Alert>
      )}

      {/* Inventory Table */}
      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Product</strong></TableCell>
              <TableCell><strong>SKU</strong></TableCell>
              <TableCell><strong>Current Stock</strong></TableCell>
              <TableCell><strong>CBU in Hand</strong></TableCell>
              <TableCell><strong>Kits in Factory</strong></TableCell>
              <TableCell><strong>Safety Stock</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
              <TableCell><strong>Actions</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {inventory.map((item) => (
              <TableRow 
                key={item.product_id} 
                hover
                sx={{ 
                  backgroundColor: item.stock_status === 'Low' ? 'rgba(255, 0, 0, 0.04)' : 'inherit'
                }}
              >
                <TableCell>
                  <Typography fontWeight="medium">
                    {item.product_name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip label={item.product_sku} size="small" variant="outlined" />
                </TableCell>
                <TableCell>
                  <Typography 
                    fontWeight="bold"
                    color={item.current_stock === 0 ? 'error.main' : 'inherit'}
                  >
                    {item.current_stock.toLocaleString()}
                  </Typography>
                </TableCell>
                <TableCell>{item.cbu_in_hand}</TableCell>
                <TableCell>{item.kits_in_factory}</TableCell>
                <TableCell>{item.safety_stock_days} days</TableCell>
                <TableCell>
                  <Chip 
                    label={item.stock_status} 
                    color={item.stock_status === 'Low' ? 'error' : 'success'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton 
                    color="primary" 
                    onClick={() => openUpdateDialog(item)}
                    title="Update Inventory"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton 
                    color="secondary" 
                    onClick={() => openSubtractDialog(item)}
                    title="Subtract Inventory"
                  >
                    <RemoveIcon />
                  </IconButton>
                  <IconButton 
                    color="error" 
                    onClick={() => handleDelete(item.product_id, item.product_name)}
                    title="Delete Inventory Record"
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {inventory.length === 0 && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <Typography color="textSecondary">
              No inventory records found.
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Update Inventory Dialog */}
      <Dialog open={updateDialogOpen} onClose={() => setUpdateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Update Inventory - {selectedProduct?.product_name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Current Stock"
              type="number"
              value={updateForm.quantity}
              onChange={(e) => setUpdateForm({ ...updateForm, quantity: parseInt(e.target.value) || 0 })}
              fullWidth
            />
            <TextField
              label="CBU in Hand"
              type="number"
              value={updateForm.cbu_in_hand}
              onChange={(e) => setUpdateForm({ ...updateForm, cbu_in_hand: parseInt(e.target.value) || 0 })}
              fullWidth
            />
            <TextField
              label="Kits in Factory"
              type="number"
              value={updateForm.kits_in_factory}
              onChange={(e) => setUpdateForm({ ...updateForm, kits_in_factory: parseInt(e.target.value) || 0 })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpdateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleUpdateInventory} variant="contained">
            Update Inventory
          </Button>
        </DialogActions>
      </Dialog>

      {/* Subtract Inventory Dialog */}
      <Dialog open={subtractDialogOpen} onClose={() => setSubtractDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Subtract Inventory - {selectedProduct?.product_name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              Current Stock: {selectedProduct?.current_stock}
            </Typography>
            <TextField
              label="Quantity to Subtract"
              type="number"
              value={subtractForm.quantity}
              onChange={(e) => setSubtractForm({ quantity: parseInt(e.target.value) || 0 })}
              fullWidth
              inputProps={{ max: selectedProduct?.current_stock }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSubtractDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleSubtractInventory} 
            variant="contained"
            disabled={subtractForm.quantity > (selectedProduct?.current_stock || 0)}
          >
            Subtract Inventory
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={4000} 
        onClose={handleCloseSnackbar}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}