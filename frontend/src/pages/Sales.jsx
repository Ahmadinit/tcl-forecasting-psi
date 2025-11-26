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
  Grid,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Alert,
  Tabs,
  Tab,
  Divider
} from "@mui/material";
import {
  Add as AddIcon,
  TrendingUp as TrendingIcon,
  Store as StoreIcon,
  ShoppingCart as ShoppingIcon
} from "@mui/icons-material";
import { 
  listModels, 
  addSale, 
  listSales, 
  getSalesByModel,
  getSalesSummary,
  getWeeklySales,
  getMultiChannelSales
} from "../services/api";

export default function Sales() {
  const [models, setModels] = useState([]);
  const [sales, setSales] = useState([]);
  const [salesSummary, setSalesSummary] = useState([]);
  const [weeklySales, setWeeklySales] = useState(null);
  const [multiChannelData, setMultiChannelData] = useState(null);
  
  // Form state
  const [form, setForm] = useState({
    product_id: "",
    quantity: 0,
    sale_date: new Date().toISOString().split('T')[0],
    channel: "all"
  });
  
  // Filters
  const [selectedProduct, setSelectedProduct] = useState("");
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7) + "-01");
  const [tabValue, setTabValue] = useState(0);
  
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadModels();
    loadSales();
    loadSalesSummary();
  }, []);

  useEffect(() => {
    if (selectedProduct) {
      loadSalesByModel();
      loadWeeklySales();
    }
  }, [selectedProduct]);

  useEffect(() => {
    if (selectedProduct && selectedMonth) {
      loadMultiChannelSales();
    }
  }, [selectedProduct, selectedMonth]);

  const loadModels = async () => {
    try {
      const res = await listModels({ active_only: true });
      setModels(res.data || []);
    } catch (err) {
      console.error("Failed to load models", err);
    }
  };

  const loadSales = async () => {
    try {
      const res = await listSales({ limit: 50 });
      setSales(res.data || []);
    } catch (err) {
      console.error("Failed to load sales", err);
      setSales([]);
    }
  };

  const loadSalesSummary = async () => {
    try {
      const res = await getSalesSummary();
      setSalesSummary(res.data || []);
    } catch (err) {
      console.error("Failed to load sales summary", err);
      setSalesSummary([]);
    }
  };

  const loadSalesByModel = async () => {
    if (!selectedProduct) return;
    try {
      const res = await getSalesByModel(parseInt(selectedProduct));
      setSales(res.data || []);
    } catch (err) {
      console.error("Failed to load sales by model", err);
      setSales([]);
    }
  };

  const loadWeeklySales = async () => {
    if (!selectedProduct) return;
    try {
      const res = await getWeeklySales(parseInt(selectedProduct), 8);
      setWeeklySales(res.data);
    } catch (err) {
      console.error("Failed to load weekly sales", err);
      setWeeklySales(null);
    }
  };

  const loadMultiChannelSales = async () => {
    if (!selectedProduct || !selectedMonth) return;
    try {
      const res = await getMultiChannelSales(parseInt(selectedProduct), selectedMonth);
      setMultiChannelData(res.data);
    } catch (err) {
      console.error("Failed to load multi-channel sales", err);
      setMultiChannelData(null);
    }
  };

  const handleSubmit = async () => {
    if (!form.product_id || !form.quantity) {
      alert("Please fill in product and quantity");
      return;
    }

    setLoading(true);
    try {
      await addSale({
        product_id: parseInt(form.product_id),
        quantity: parseInt(form.quantity),
        sale_date: form.sale_date,
        channel: form.channel
      });
      
      alert("Sale added successfully!");
      setForm({
        product_id: "",
        quantity: 0,
        sale_date: new Date().toISOString().split('T')[0],
        channel: "all"
      });
      
      loadSales();
      loadSalesSummary();
      if (selectedProduct) {
        loadSalesByModel();
        loadWeeklySales();
      }
    } catch (err) {
      console.error("Add sale failed", err);
      alert("Failed to add sale: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const channels = [
    { value: "all", label: "All Channels" },
    { value: "ecommerce", label: "E-commerce" },
    { value: "A101", label: "A101" },
    { value: "wholesale", label: "Wholesale" }
  ];

  const selectedProductData = models.find(m => m.id === parseInt(selectedProduct));

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Sales Management
      </Typography>
      <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
        Record actual sales data (used for purchase forecasting)
      </Typography>

      <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
        <Tab label="Add Sales" />
        <Tab label="Sales Data" />
        <Tab label="Multi-Channel Analysis" />
      </Tabs>

      {/* Tab 1: Add Sales */}
      {tabValue === 0 && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <AddIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Add New Sale</Typography>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Product</InputLabel>
                <Select
                  value={form.product_id}
                  onChange={(e) => setForm({ ...form, product_id: e.target.value })}
                  label="Product"
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
            </Grid>

            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                type="date"
                label="Sale Date"
                value={form.sale_date}
                onChange={(e) => setForm({ ...form, sale_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Channel</InputLabel>
                <Select
                  value={form.channel}
                  onChange={(e) => setForm({ ...form, channel: e.target.value })}
                  label="Channel"
                >
                  {channels.map((ch) => (
                    <MenuItem key={ch.value} value={ch.value}>
                      {ch.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                type="number"
                label="Quantity"
                value={form.quantity}
                onChange={(e) => setForm({ ...form, quantity: parseInt(e.target.value) || 0 })}
                inputProps={{ min: 0 }}
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={loading || !form.product_id || !form.quantity}
                startIcon={<AddIcon />}
              >
                {loading ? "Adding..." : "Add Sale"}
              </Button>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Tab 2: Sales Data */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Filters</Typography>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Select Product</InputLabel>
                <Select
                  value={selectedProduct}
                  onChange={(e) => {
                    setSelectedProduct(e.target.value);
                    if (e.target.value) {
                      setForm({ ...form, product_id: e.target.value });
                    }
                  }}
                  label="Select Product"
                >
                  <MenuItem value="">
                    <em>All Products</em>
                  </MenuItem>
                  {models.map((m) => (
                    <MenuItem key={m.id} value={m.id.toString()}>
                      {m.sku} - {m.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Paper>

            {salesSummary.length > 0 && (
              <Paper sx={{ p: 2, mt: 2 }}>
                <Typography variant="h6" gutterBottom>Sales Summary</Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Product</TableCell>
                        <TableCell>Total Qty</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {salesSummary.map((item) => (
                        <TableRow key={item.product_id}>
                          <TableCell>{item.product_name}</TableCell>
                          <TableCell>{item.total_quantity}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Paper>
            )}
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                {selectedProduct ? `Sales for ${selectedProductData?.name || 'Product'}` : 'All Sales'}
              </Typography>

              {weeklySales && selectedProduct && (
                <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Weekly Sales Trend (Last 8 Weeks)
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {weeklySales.weekly_sales?.map((w, i) => (
                      <Chip
                        key={i}
                        label={`Week ${w.week}: ${w.quantity}`}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {sales.length === 0 ? (
                <Alert severity="info">No sales data found</Alert>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Product</TableCell>
                        <TableCell>Quantity</TableCell>
                        <TableCell>Channel</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {sales.map((sale) => (
                        <TableRow key={sale.id} hover>
                          <TableCell>
                            {new Date(sale.sale_date).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {sale.product_name || 'Unknown'}
                            </Typography>
                          </TableCell>
                          <TableCell>{sale.quantity}</TableCell>
                          <TableCell>
                            <Chip
                              label={sale.channel}
                              size="small"
                              variant="outlined"
                              color={
                                sale.channel === 'ecommerce' ? 'primary' :
                                sale.channel === 'A101' ? 'secondary' :
                                sale.channel === 'wholesale' ? 'default' : 'default'
                              }
                            />
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
      )}

      {/* Tab 3: Multi-Channel Analysis */}
      {tabValue === 2 && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <StoreIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Multi-Channel Sales Analysis</Typography>
          </Box>

          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Select Product</InputLabel>
                <Select
                  value={selectedProduct}
                  onChange={(e) => setSelectedProduct(e.target.value)}
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
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="month"
                label="Target Month"
                value={selectedMonth.slice(0, 7)}
                onChange={(e) => setSelectedMonth(e.target.value + "-01")}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>

          {multiChannelData ? (
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <ShoppingIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="subtitle2" color="textSecondary">
                        E-commerce
                      </Typography>
                    </Box>
                    <Typography variant="h4">{multiChannelData.ecommerce}</Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <StoreIcon sx={{ mr: 1, color: 'secondary.main' }} />
                      <Typography variant="subtitle2" color="textSecondary">
                        A101
                      </Typography>
                    </Box>
                    <Typography variant="h4">{multiChannelData.A101}</Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <TrendingIcon sx={{ mr: 1, color: 'success.main' }} />
                      <Typography variant="subtitle2" color="textSecondary">
                        Wholesale
                      </Typography>
                    </Box>
                    <Typography variant="h4">{multiChannelData.wholesale}</Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
              </Grid>

              <Grid item xs={12}>
                <Card variant="outlined" sx={{ bgcolor: 'primary.light', color: 'primary.contrastText' }}>
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      Total All Channels
                    </Typography>
                    <Typography variant="h3" fontWeight="bold">
                      {multiChannelData.total_all_channels}
                    </Typography>
                    <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                      Month: {multiChannelData.month}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          ) : (
            <Alert severity="info">
              Select a product and month to view multi-channel sales analysis
            </Alert>
          )}
        </Paper>
      )}
    </Box>
  );
}
