// frontend/src/pages/PurchaseOrders.jsx
import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableContainer,
  Chip,
  Alert,
  Grid,
  Card,
  CardContent,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Slider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip
} from "@mui/material";
import {
  TrendingUp,
  Inventory as InventoryIcon,
  ShoppingCart,
  CalendarToday,
  Download,
  PictureAsPdf,
  PlayArrow,
  FilterList
} from "@mui/icons-material";
import { 
  listModels, 
  listPOs, 
  createPO, 
  forecastPO, 
  getInventory,
  updatePOStage,
  generateWeeklyPOs,
  exportPOExcel,
  exportPOPDF
} from "../services/api";

const PO_STAGES = ["CKD Prepared", "Booking", "Shipped", "Customs", "Assembly"];

export default function PurchaseOrders() {
  const [models, setModels] = useState([]);
  const [pos, setPos] = useState([]);
  const [filteredPos, setFilteredPos] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState("");
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [stageFilter, setStageFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedPO, setSelectedPO] = useState(null);
  const [stageDialogOpen, setStageDialogOpen] = useState(false);
  const [generatingPOs, setGeneratingPOs] = useState(false);

  useEffect(() => {
    loadModels();
    loadPOs();
  }, []);

  const loadModels = async () => {
    try {
      const res = await listModels({ active_only: true });
      setModels(res.data || []);
    } catch (err) {
      console.error("Failed to load models", err);
    }
  };

  const loadPOs = async () => {
    try {
      const params = {};
      if (stageFilter) params.stage = stageFilter;
      if (statusFilter) params.status = statusFilter;
      
      const res = await listPOs(params);
      setPos(res.data || []);
      setFilteredPos(res.data || []);
    } catch (err) {
      console.error("Failed to load POs", err);
      setPos([]);
      setFilteredPos([]);
    }
  };

  useEffect(() => {
    loadPOs();
  }, [stageFilter, statusFilter]);

  const handleStageUpdate = async (poId, newStage) => {
    try {
      await updatePOStage(poId, newStage);
      await loadPOs();
      setStageDialogOpen(false);
      setSelectedPO(null);
    } catch (err) {
      console.error("Failed to update stage", err);
      alert("Failed to update PO stage: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleGenerateWeeklyPOs = async () => {
    if (!confirm("Generate weekly POs for all products? This will create POs for the current week (Saturday).")) {
      return;
    }
    
    setGeneratingPOs(true);
    try {
      const res = await generateWeeklyPOs();
      alert(`Generated ${res.data.generated_count} purchase orders. ${res.data.skipped_count} were skipped (already exist).`);
      await loadPOs();
    } catch (err) {
      console.error("Failed to generate POs", err);
      alert("Failed to generate weekly POs: " + (err.response?.data?.detail || err.message));
    } finally {
      setGeneratingPOs(false);
    }
  };

  const handleExportExcel = async () => {
    try {
      const response = await exportPOExcel(stageFilter || undefined, statusFilter || undefined);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `purchase_orders_${stageFilter || 'all'}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Export failed", err);
      alert("Failed to export to Excel");
    }
  };

  const handleExportPDF = async () => {
    try {
      const response = await exportPOPDF(stageFilter || undefined, statusFilter || undefined);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `purchase_orders_${stageFilter || 'all'}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Export failed", err);
      alert("Failed to export to PDF");
    }
  };

  const getStageValue = (stage) => {
    return PO_STAGES.indexOf(stage || "CKD Prepared");
  };

  const handleForecast = async () => {
    if (!selectedProductId) {
      alert("Please select a product first");
      return;
    }

    setForecastLoading(true);
    try {
      // Get purchase forecast based on SALES DATA and INVENTORY
      const res = await forecastPO(selectedProductId, 8, 10);
      setForecast(res.data);
    } catch (err) {
      console.error("Forecast error", err);
      alert("Failed to generate forecast. Make sure you have sales data for this product.");
      setForecast(null);
    } finally {
      setForecastLoading(false);
    }
  };

  const handleCreatePOFromForecast = async () => {
    if (!forecast || !selectedProductId) return;

    try {
      const today = new Date();
      const orderWeek = new Date(forecast.recommended_order_week);
      
      const poData = {
        product_id: parseInt(selectedProductId),
        quantity: forecast.suggested_quantity,
        order_week: orderWeek.toISOString().split('T')[0],
        etd: forecast.recommended_etd,
        eta: forecast.recommended_eta,
        status: "suggested",
        shipping_mode: "CKD F"
      };

      await createPO(poData);
      alert("Purchase Order created successfully!");
      loadPOs();
      setForecast(null);
    } catch (err) {
      console.error("Create PO failed", err);
      alert("Failed to create PO: " + (err.response?.data?.detail || err.message));
    }
  };

  const selectedProduct = models.find(m => m.id === parseInt(selectedProductId));

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Purchase Orders & Forecast
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
        Forecast purchases based on actual sales data and current inventory
      </Typography>

      <Grid container spacing={3}>
        {/* Forecast Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Purchase Forecast
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Select a product to generate purchase forecast based on sales trends
            </Typography>

            <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Select Product</InputLabel>
                <Select
                  value={selectedProductId}
                  onChange={(e) => {
                    setSelectedProductId(e.target.value);
                    setForecast(null);
                  }}
                  label="Select Product"
                >
                  <MenuItem value="">
                    <em>-- Select Product --</em>
                  </MenuItem>
                  {models.map((m) => (
                    <MenuItem key={m.id} value={m.id.toString()}>
                      {m.sku} - {m.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button
                variant="contained"
                onClick={handleForecast}
                disabled={!selectedProductId || forecastLoading}
                startIcon={<TrendingUp />}
              >
                {forecastLoading ? "Calculating..." : "Get Forecast"}
              </Button>
            </Box>

            {forecast && (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Forecast based on {forecast.data_points_used} weeks of sales data
                  ({forecast.confidence_level} confidence)
                </Alert>

                <Grid container spacing={2} sx={{ mb: 2 }}>
                  <Grid item xs={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="caption" color="textSecondary">
                          Current Stock
                        </Typography>
                        <Typography variant="h5">
                          {forecast.current_stock}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="caption" color="textSecondary">
                          Weekly Demand (Forecasted)
                        </Typography>
                        <Typography variant="h5">
                          {forecast.forecasted_weekly_demand.toFixed(1)}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="caption" color="textSecondary">
                          Safety Stock
                        </Typography>
                        <Typography variant="h5">
                          {forecast.safety_stock}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6}>
                    <Card variant="outlined" sx={{ bgcolor: "primary.light", color: "primary.contrastText" }}>
                      <CardContent>
                        <Typography variant="caption">
                          Suggested Purchase Qty
                        </Typography>
                        <Typography variant="h5" fontWeight="bold">
                          {forecast.suggested_quantity}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                <Paper sx={{ p: 2, bgcolor: "grey.50", mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Recommended Timeline
                  </Typography>
                  <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <CalendarToday fontSize="small" />
                      <Typography variant="body2">
                        Order Week: <strong>{new Date(forecast.recommended_order_week).toLocaleDateString()}</strong>
                      </Typography>
                    </Box>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <ShoppingCart fontSize="small" />
                      <Typography variant="body2">
                        ETD: <strong>{new Date(forecast.recommended_etd).toLocaleDateString()}</strong>
                      </Typography>
                    </Box>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <InventoryIcon fontSize="small" />
                      <Typography variant="body2">
                        ETA: <strong>{new Date(forecast.recommended_eta).toLocaleDateString()}</strong>
                      </Typography>
                    </Box>
                  </Box>
                </Paper>

                <Button
                  variant="contained"
                  color="primary"
                  fullWidth
                  onClick={handleCreatePOFromForecast}
                  startIcon={<ShoppingCart />}
                >
                  Create PO from Forecast
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Purchase Orders List */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Purchase Orders
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Tooltip title="Generate Weekly POs">
                  <IconButton 
                    color="primary" 
                    onClick={handleGenerateWeeklyPOs}
                    disabled={generatingPOs}
                  >
                    <PlayArrow />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Export to Excel">
                  <IconButton color="success" onClick={handleExportExcel}>
                    <Download />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Export to PDF">
                  <IconButton color="error" onClick={handleExportPDF}>
                    <PictureAsPdf />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>

            {/* Filters */}
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Filter by Stage</InputLabel>
                <Select
                  value={stageFilter}
                  onChange={(e) => setStageFilter(e.target.value)}
                  label="Filter by Stage"
                >
                  <MenuItem value="">All Stages</MenuItem>
                  {PO_STAGES.map(stage => (
                    <MenuItem key={stage} value={stage}>{stage}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Filter by Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  label="Filter by Status"
                >
                  <MenuItem value="">All Statuses</MenuItem>
                  <MenuItem value="suggested">Suggested</MenuItem>
                  <MenuItem value="ordered">Ordered</MenuItem>
                  <MenuItem value="shipped">Shipped</MenuItem>
                  <MenuItem value="delivered">Delivered</MenuItem>
                  <MenuItem value="cancelled">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Box>

            {filteredPos.length === 0 ? (
              <Alert severity="info">No purchase orders found</Alert>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>PO Number</TableCell>
                      <TableCell>Product</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Stage</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Order Week</TableCell>
                      <TableCell>ETA</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredPos.map((po) => (
                      <TableRow key={po.id} hover>
                        <TableCell>{po.po_number || `PO-${po.id}`}</TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {po.product_name}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {po.product_sku}
                          </Typography>
                        </TableCell>
                        <TableCell>{po.quantity}</TableCell>
                        <TableCell>
                          <Chip
                            label={po.stage || "CKD Prepared"}
                            size="small"
                            color="primary"
                            onClick={() => {
                              setSelectedPO(po);
                              setStageDialogOpen(true);
                            }}
                            sx={{ cursor: 'pointer' }}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={po.status}
                            size="small"
                            color={
                              po.status === "delivered" ? "success" :
                              po.status === "shipped" ? "info" :
                              po.status === "ordered" ? "primary" :
                              "default"
                            }
                          />
                        </TableCell>
                        <TableCell>
                          {po.order_week ? new Date(po.order_week).toLocaleDateString() : "-"}
                        </TableCell>
                        <TableCell>
                          {po.eta ? new Date(po.eta).toLocaleDateString() : "-"}
                        </TableCell>
                        <TableCell>
                          <Button
                            size="small"
                            onClick={() => {
                              setSelectedPO(po);
                              setStageDialogOpen(true);
                            }}
                          >
                            Update Stage
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Stage Update Dialog */}
      <Dialog open={stageDialogOpen} onClose={() => setStageDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Update PO Stage</DialogTitle>
        <DialogContent>
          {selectedPO && (
            <Box>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                PO: {selectedPO.po_number || `PO-${selectedPO.id}`} - {selectedPO.product_name}
              </Typography>
              <Typography variant="h6" gutterBottom sx={{ mt: 2, mb: 3 }}>
                Current Stage: {selectedPO.stage || "CKD Prepared"}
              </Typography>
              <Typography gutterBottom>Select New Stage:</Typography>
              <Slider
                value={getStageValue(selectedPO.stage)}
                min={0}
                max={PO_STAGES.length - 1}
                step={1}
                marks={PO_STAGES.map((stage, index) => ({ value: index, label: stage }))}
                onChange={(e, value) => {
                  const newStage = PO_STAGES[value];
                  handleStageUpdate(selectedPO.id, newStage);
                }}
                sx={{ mt: 3 }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStageDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
