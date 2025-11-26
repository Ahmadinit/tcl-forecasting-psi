import React, { useEffect, useState } from "react";
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Alert,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  TextField
} from "@mui/material";
import {
  Inventory as InventoryIcon,
  ShoppingCart as PurchaseIcon,
  LocalShipping as ShippingIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon
} from "@mui/icons-material";
import { 
  getInventory, 
  getLowStockAlerts, 
  listPOs, 
  listSales,
  getSalesSummary,
  listModels,
  calculateMonthlyPSI,
  calculateNPlus3Stock,
  listMonthlyPlans,
  getDashboardStats,
  getInventoryHealthChart,
  getSalesTrendChart,
  getPOForecastVsActualChart,
  getShipmentStagesChart,
  getLeadTimePerformanceChart
} from "../services/api";
import { Pie, Line, Bar, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    totalInventory: 0,
    lowStockItems: 0,
    pendingPOs: 0,
    activeShipments: 0,
    monthlySales: 0,
    criticalProducts: 0,
    warningProducts: 0,
    safeProducts: 0,
    weeklySales: 0
  });
  const [lowStockAlerts, setLowStockAlerts] = useState([]);
  const [recentSales, setRecentSales] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // PSI Dashboard state
  const [selectedProduct, setSelectedProduct] = useState("");
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7) + "-01");
  const [psiData, setPsiData] = useState(null);
  const [nPlus3Data, setNPlus3Data] = useState(null);
  const [products, setProducts] = useState([]);
  const [monthlyPlans, setMonthlyPlans] = useState([]);
  const [tabValue, setTabValue] = useState(0);
  const [loadingPSI, setLoadingPSI] = useState(false);
  
  // Chart data
  const [inventoryHealthData, setInventoryHealthData] = useState(null);
  const [salesTrendData, setSalesTrendData] = useState(null);
  const [poForecastData, setPoForecastData] = useState(null);
  const [shipmentStagesData, setShipmentStagesData] = useState(null);
  const [leadTimeData, setLeadTimeData] = useState(null);

  useEffect(() => {
    loadDashboardData();
    loadProducts();
  }, []);

  useEffect(() => {
    if (selectedProduct && selectedMonth) {
      loadPSIData();
      loadNPlus3Data();
    }
  }, [selectedProduct, selectedMonth]);

  const loadProducts = async () => {
    try {
      const res = await listModels({ active_only: true });
      setProducts(res.data || []);
      if (res.data && res.data.length > 0) {
        setSelectedProduct(res.data[0].id.toString());
      }
    } catch (err) {
      console.error("Failed to load products", err);
    }
  };

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [
        dashboardStatsResponse,
        inventoryHealthResponse,
        salesTrendResponse,
        poForecastResponse,
        shipmentStagesResponse,
        leadTimeResponse,
        inventoryResponse,
        lowStockResponse,
        poResponse,
        salesResponse,
        salesSummaryResponse,
        monthlyPlansResponse
      ] = await Promise.all([
        getDashboardStats(),
        getInventoryHealthChart(),
        getSalesTrendChart(12),
        getPOForecastVsActualChart(12),
        getShipmentStagesChart(),
        getLeadTimePerformanceChart(),
        getInventory(),
        getLowStockAlerts(),
        listPOs(),
        listSales({ limit: 10 }),
        getSalesSummary(),
        listMonthlyPlans()
      ]);

      // Update stats from dashboard API
      const dashboardStats = dashboardStatsResponse.data || {};
      setStats({
        totalProducts: dashboardStats.total_products || 0,
        totalInventory: inventoryResponse.data?.reduce((sum, item) => sum + (item.current_stock || 0), 0) || 0,
        lowStockItems: dashboardStats.critical_products || 0,
        pendingPOs: dashboardStats.pending_pos || 0,
        activeShipments: poResponse.data?.filter(po => po.status === 'shipped').length || 0,
        monthlySales: salesSummaryResponse.data?.reduce((sum, item) => sum + (item.total_quantity || 0), 0) || 0,
        criticalProducts: dashboardStats.critical_products || 0,
        warningProducts: dashboardStats.warning_products || 0,
        safeProducts: dashboardStats.safe_products || 0,
        weeklySales: dashboardStats.weekly_sales || 0
      });

      // Set chart data
      setInventoryHealthData(inventoryHealthResponse.data);
      setSalesTrendData(salesTrendResponse.data);
      setPoForecastData(poForecastResponse.data);
      setShipmentStagesData(shipmentStagesResponse.data);
      setLeadTimeData(leadTimeResponse.data);

      const inventory = inventoryResponse.data || [];
      const lowStockAlerts = lowStockResponse.data || [];
      const recentSales = salesResponse.data || [];
      const plans = monthlyPlansResponse.data || [];

      setLowStockAlerts(lowStockAlerts.slice(0, 5));
      setRecentSales(recentSales);
      setMonthlyPlans(plans);

    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadPSIData = async () => {
    if (!selectedProduct) return;
    setLoadingPSI(true);
    try {
      const res = await calculateMonthlyPSI(parseInt(selectedProduct), selectedMonth);
      setPsiData(res.data);
    } catch (err) {
      console.error("Failed to load PSI data", err);
      setPsiData(null);
    } finally {
      setLoadingPSI(false);
    }
  };

  const loadNPlus3Data = async () => {
    if (!selectedProduct) return;
    try {
      const res = await calculateNPlus3Stock(parseInt(selectedProduct));
      setNPlus3Data(res.data);
    } catch (err) {
      // Suppress 422 errors (validation errors) - product might not exist or have data
      if (err.response?.status !== 422) {
        console.error("Failed to load N+3 data", err);
      }
      setNPlus3Data(null);
    }
  };

  const StatCard = ({ title, value, icon, color = "primary", subtitle }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="overline">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box sx={{ color: `${color}.main`, fontSize: 40 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>PSI Dashboard</Typography>
        <LinearProgress />
      </Box>
    );
  }

  const selectedProductData = products.find(p => p.id === parseInt(selectedProduct));

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        PSI Dashboard
      </Typography>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Total Products"
            value={stats.totalProducts}
            icon={<InventoryIcon fontSize="inherit" />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Total Inventory"
            value={stats.totalInventory.toLocaleString()}
            icon={<InventoryIcon fontSize="inherit" />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Low Stock Items"
            value={stats.lowStockItems}
            icon={<WarningIcon fontSize="inherit" />}
            color="error"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Pending POs"
            value={stats.pendingPOs}
            icon={<PurchaseIcon fontSize="inherit" />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Active Shipments"
            value={stats.activeShipments}
            icon={<ShippingIcon fontSize="inherit" />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <StatCard
            title="Monthly Sales"
            value={stats.monthlySales.toLocaleString()}
            icon={<TrendingIcon fontSize="inherit" />}
            color="secondary"
          />
        </Grid>
      </Grid>

      {/* PSI Calculation Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <AssessmentIcon sx={{ mr: 1 }} />
          <Typography variant="h6">PSI Calculations (Excel Sheet 2)</Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Select Product</InputLabel>
            <Select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              label="Select Product"
            >
              {products.map((p) => (
                <MenuItem key={p.id} value={p.id.toString()}>
                  {p.sku} - {p.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            type="month"
            label="Target Month"
            value={selectedMonth.slice(0, 7)}
            onChange={(e) => setSelectedMonth(e.target.value + "-01")}
            InputLabelProps={{ shrink: true }}
            sx={{ minWidth: 200 }}
          />
        </Box>

        {loadingPSI ? (
          <LinearProgress />
        ) : psiData ? (
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    Opening Balance
                  </Typography>
                  <Typography variant="h5">{psiData.opening_balance}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    Available Sales Inventory
                  </Typography>
                  <Typography variant="h5">{psiData.available_sales_inventory}</Typography>
                  <Typography variant="caption" color="textSecondary">
                    = Purchases ({psiData.total_weekly_purchases}) + Opening ({psiData.opening_balance})
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    W1 Purchase
                  </Typography>
                  <Typography variant="h6">{psiData.week_1_purchase}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    W2 Purchase
                  </Typography>
                  <Typography variant="h6">{psiData.week_2_purchase}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    W3 Purchase
                  </Typography>
                  <Typography variant="h6">{psiData.week_3_purchase}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    W4 Purchase
                  </Typography>
                  <Typography variant="h6">{psiData.week_4_purchase}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    Sales Forecast
                  </Typography>
                  <Typography variant="h5">{psiData.sales_forecast}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined" sx={{ bgcolor: (psiData.status || 'Unknown') === 'Healthy' ? 'success.light' : 'warning.light' }}>
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    Ending Inventory
                  </Typography>
                  <Typography variant="h5">{psiData.ending_inventory ?? 'N/A'}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined" sx={{ bgcolor: psiData.status === 'Healthy' ? 'success.light' : 'warning.light' }}>
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    DOS Days
                  </Typography>
                  <Typography variant="h5">
                    {psiData.dos_days === null || psiData.dos_days === undefined 
                      ? 'N/A' 
                      : psiData.dos_days === Infinity 
                        ? '∞' 
                        : typeof psiData.dos_days === 'number' 
                          ? psiData.dos_days.toFixed(1) 
                          : 'N/A'}
                  </Typography>
                  <Chip 
                    label={psiData.status || 'Unknown'} 
                    size="small" 
                    color={(psiData.status || 'Unknown') === 'Healthy' ? 'success' : 'warning'}
                    sx={{ mt: 1 }}
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        ) : (
          <Alert severity="info">Select a product and month to view PSI calculations</Alert>
        )}
      </Paper>

      {/* N+3 Stock Projection */}
      {nPlus3Data && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <TimelineIcon sx={{ mr: 1 }} />
            <Typography variant="h6">N+3 Rolling Stock (Excel Sheet 3)</Typography>
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    CBU in Hand
                  </Typography>
                  <Typography variant="h6">{nPlus3Data.cbu_in_hand}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    Kits in Factory
                  </Typography>
                  <Typography variant="h6">{nPlus3Data.kits_in_factory}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    Sea Shipping
                  </Typography>
                  <Typography variant="h6">{nPlus3Data.sea_shipping}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined" sx={{ bgcolor: 'primary.light', color: 'primary.contrastText' }}>
                <CardContent>
                  <Typography variant="subtitle2" gutterBottom>
                    End-to-End Inventory
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {nPlus3Data.end_to_end_inventory}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Paper>
      )}

      <Grid container spacing={3}>
        {/* Low Stock Alerts */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom color="error">
              <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Low Stock Alerts
            </Typography>
            {lowStockAlerts.length === 0 ? (
              <Alert severity="success">No low stock items</Alert>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Product</TableCell>
                      <TableCell>Current Stock</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {lowStockAlerts.map((alert) => (
                      <TableRow key={alert.product_id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {alert.product_name}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {alert.product_sku}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box>
                            <Typography variant="body2">
                              {alert.current_stock} units
                            </Typography>
                            <Typography variant="caption" color="textSecondary">
                              Safety: {alert.safety_stock_days} days
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={alert.status} 
                            color={alert.status === 'Critical' ? 'error' : 'warning'}
                            size="small"
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

        {/* Recent Sales */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Sales
            </Typography>
            {recentSales.length === 0 ? (
              <Alert severity="info">No recent sales</Alert>
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
                    {recentSales.map((sale) => (
                      <TableRow key={sale.id} hover>
                        <TableCell>
                          {new Date(sale.sale_date).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {sale.product_name}
                          </Typography>
                        </TableCell>
                        <TableCell>{sale.quantity}</TableCell>
                        <TableCell>
                          <Chip 
                            label={sale.channel} 
                            size="small"
                            variant="outlined"
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

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Inventory Health Pie Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Inventory Health
            </Typography>
            {inventoryHealthData ? (
              <Box sx={{ height: 300 }}>
                <Pie
                  data={{
                    labels: inventoryHealthData.labels,
                    datasets: [{
                      data: inventoryHealthData.data,
                      backgroundColor: inventoryHealthData.colors
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' }
                    }
                  }}
                />
              </Box>
            ) : (
              <Alert severity="info">Loading chart data...</Alert>
            )}
          </Paper>
        </Grid>

        {/* Shipment Stages Donut Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Shipment Stage Distribution
            </Typography>
            {shipmentStagesData ? (
              <Box sx={{ height: 300 }}>
                <Doughnut
                  data={{
                    labels: shipmentStagesData.labels,
                    datasets: [{
                      data: shipmentStagesData.data,
                      backgroundColor: shipmentStagesData.colors
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' }
                    }
                  }}
                />
              </Box>
            ) : (
              <Alert severity="info">Loading chart data...</Alert>
            )}
          </Paper>
        </Grid>

        {/* Sales Trend Line Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Sales Trend (Last 12 Weeks)
            </Typography>
            {salesTrendData ? (
              <Box sx={{ height: 300 }}>
                <Line
                  data={{
                    labels: salesTrendData.labels.map(d => new Date(d).toLocaleDateString()),
                    datasets: [{
                      label: 'Weekly Sales',
                      data: salesTrendData.data,
                      borderColor: 'rgb(75, 192, 192)',
                      backgroundColor: 'rgba(75, 192, 192, 0.2)',
                      tension: 0.1
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false }
                    },
                    scales: {
                      y: { beginAtZero: true }
                    }
                  }}
                />
              </Box>
            ) : (
              <Alert severity="info">Loading chart data...</Alert>
            )}
          </Paper>
        </Grid>

        {/* PO Forecast vs Actual Bar Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              PO Forecast vs Actual
            </Typography>
            {poForecastData ? (
              <Box sx={{ height: 300 }}>
                <Bar
                  data={{
                    labels: poForecastData.labels.map(d => new Date(d).toLocaleDateString()),
                    datasets: [
                      {
                        label: 'Forecasted',
                        data: poForecastData.forecasted,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)'
                      },
                      {
                        label: 'Actual',
                        data: poForecastData.actual,
                        backgroundColor: 'rgba(255, 99, 132, 0.5)'
                      }
                    ]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' }
                    },
                    scales: {
                      y: { beginAtZero: true }
                    }
                  }}
                />
              </Box>
            ) : (
              <Alert severity="info">Loading chart data...</Alert>
            )}
          </Paper>
        </Grid>

        {/* Lead Time Performance Histogram */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Lead Time Performance
            </Typography>
            {leadTimeData ? (
              <Box>
                <Box sx={{ height: 300, mb: 2 }}>
                  <Bar
                    data={{
                      labels: leadTimeData.labels,
                      datasets: [{
                        label: 'Number of Deliveries',
                        data: leadTimeData.data,
                        backgroundColor: 'rgba(153, 102, 255, 0.5)'
                      }]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { display: false }
                      },
                      scales: {
                        y: { beginAtZero: true }
                      }
                    }}
                  />
                </Box>
                <Typography variant="body2" color="textSecondary">
                  Average Lead Time: {leadTimeData.average_lead_time?.toFixed(1) || 'N/A'} days | 
                  Total Deliveries: {leadTimeData.total_deliveries || 0}
                </Typography>
              </Box>
            ) : (
              <Alert severity="info">Loading chart data...</Alert>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Color-coded Inventory List */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Inventory Status (Color-Coded)
        </Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Product</TableCell>
                <TableCell>Current Stock</TableCell>
                <TableCell>Safety Stock</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {lowStockAlerts.map((item) => {
                const isCritical = item.current_stock <= (item.safety_stock_days || 0);
                const isWarning = !isCritical && item.current_stock <= (item.safety_stock_days || 0) * 1.2;
                const bgColor = isCritical ? 'error.light' : isWarning ? 'warning.light' : 'success.light';
                
                return (
                  <TableRow 
                    key={item.product_id} 
                    sx={{ bgcolor: bgColor }}
                    hover
                  >
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {item.product_name}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {item.product_sku}
                      </Typography>
                    </TableCell>
                    <TableCell>{item.current_stock}</TableCell>
                    <TableCell>{item.safety_stock_days} days</TableCell>
                    <TableCell>
                      <Chip
                        label={isCritical ? 'Critical' : isWarning ? 'Warning' : 'Safe'}
                        size="small"
                        color={isCritical ? 'error' : isWarning ? 'warning' : 'success'}
                      />
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
