// Complete API service for all modules
import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 10000,
});

export default API;

// Add response interceptor for better error handling
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      console.error('Backend server is not running. Please start the FastAPI server.');
    }
    return Promise.reject(error);
  }
);

// Auth
export const authCreate = (username, password) =>
  API.post("/auth/create", { username, password });
export const authLogin = (payload) => API.post("/auth/login", payload);
export const checkAuthSetup = () => API.get("/auth/check-setup");
export const getUser = (userId) => API.get(`/auth/user/${userId}`);

// Models
export const listModels = (params = {}) => API.get("/models", { params });
export const getModel = (modelId) => API.get(`/models/${modelId}`);
export const createModel = (payload) => API.post("/models", payload);
export const updateModel = (modelId, payload) => API.put(`/models/${modelId}`, payload);
export const deleteModel = (modelId) => API.delete(`/models/${modelId}`);

// Inventory
export const getInventory = (params = {}) => API.get("/inventory", { params });
export const getInventoryItem = (productId) => API.get(`/inventory/${productId}`);
export const updateInventory = (payload) => API.post("/inventory/update", payload);
export const subtractInventory = (payload) => API.post("/inventory/subtract", payload);
export const getLowStockAlerts = () => API.get("/inventory/alerts/low-stock");
export const deleteInventoryRecord = (productId) => API.delete(`/inventory/${productId}`);

// Sales
export const addSale = (payload) => API.post("/sales", payload);
export const listSales = (params = {}) => API.get("/sales", { params });
export const getSalesByModel = (modelId, params = {}) => 
  API.get(`/sales/by_model/${modelId}`, { params });
export const getSalesSummary = (params = {}) => 
  API.get("/sales/summary", { params });
export const getWeeklySales = (productId, weeks = 8) => 
  API.get("/sales/weekly", { params: { product_id: productId, weeks } });
export const updateSale = (saleId, payload) => API.put(`/sales/${saleId}`, payload);
export const deleteSalesRecord = (saleId) => API.delete(`/sales/${saleId}`);

// Purchase Orders - Forecast purchases based on SALES DATA and INVENTORY
export const listPOs = (params = {}) => API.get("/purchase", { params });
export const createPO = (payload) => API.post("/purchase/create", payload);
export const forecastPO = (productId, weeks = 8, forecastWeeks = 10) => 
  API.get("/purchase/forecast", { params: { product_id: productId, weeks, forecast_weeks: forecastWeeks } });
export const updatePO = (poId, payload) => API.put(`/purchase/${poId}`, payload);
export const deletePO = (poId) => API.delete(`/purchase/${poId}`);

// Shipments
export const listShipments = (params = {}) => API.get("/shipments", { params });
export const updateShipmentStage = (poId, stage, notes = null) => 
  API.post("/shipments/update-stage", null, { 
    params: { po_id: poId, stage, notes } 
  });
export const getShipmentStatus = (poId) => API.get(`/shipments/status/${poId}`);
export const getShipmentTimeline = (params = {}) => API.get("/shipments/timeline", { params });

// Settings
export const getSettings = () => API.get("/settings");
export const getSetting = (configKey) => API.get(`/settings/${configKey}`);
export const updateSetting = (configKey, payload) => API.put(`/settings/${configKey}`, payload);
export const createSetting = (payload) => API.post("/settings", payload);
export const deleteSetting = (configKey) => API.delete(`/settings/${configKey}`);
export const getLeadTimeSummary = () => API.get("/settings/lead-times/summary");

// Monthly Plans - PSI Dashboard (Sheet 2)
export const listMonthlyPlans = (params = {}) => API.get("/monthly-plan", { params });
export const getMonthlyPlan = (planId) => API.get(`/monthly-plan/${planId}`);
export const createMonthlyPlan = (payload) => API.post("/monthly-plan/create", payload);
export const updateMonthlyPlan = (planId, payload) => API.put(`/monthly-plan/${planId}`, payload);
export const deleteMonthlyPlan = (planId) => API.delete(`/monthly-plan/${planId}`);
export const autoGenerateMonthlyPlan = (productId, planMonth, version = "v1.0") =>
  API.post("/monthly-plan/auto-generate", null, { params: { product_id: productId, plan_month: planMonth, version } });

// PSI Calculations (from inventory router)
export const calculateMonthlyPSI = (productId, targetMonth) =>
  API.get("/inventory/psi/monthly", { params: { product_id: productId, target_month: targetMonth } });
export const calculateNPlus3Stock = (productId) =>
  API.get("/inventory/n-plus-3-stock", { params: { product_id: productId } });
export const getEndToEndInventory = (productId) =>
  API.get("/inventory/end-to-end", { params: { product_id: productId } });
export const getMultiChannelSales = (productId, targetMonth) =>
  API.get("/inventory/sales/multi-channel", { params: { product_id: productId, target_month: targetMonth } });

// Product Configuration
export const updateProductConfig = (payload) => API.put("/inventory/product-config", payload);

// Weekly PO Generation
export const generateWeeklyPOs = (orderWeek) =>
  API.post("/purchase/generate-weekly", null, { params: { order_week: orderWeek } });
export const generateAnnualPOs = (year) =>
  API.post("/purchase/generate-annual", null, { params: { year } });

// PO Stage Management
export const updatePOStage = (poId, stage, notes) =>
  API.post(`/purchase/${poId}/stage`, null, { params: { stage, notes } });
export const getPOTimeline = (poId) => API.get(`/purchase/${poId}/timeline`);

// Dashboard Charts and Stats
export const getDashboardStats = () => API.get("/dashboard/stats");
export const getInventoryHealthChart = () => API.get("/dashboard/charts/inventory-health");
export const getSalesTrendChart = (weeks, productId) =>
  API.get("/dashboard/charts/sales-trend", { params: { weeks, product_id: productId } });
export const getPOForecastVsActualChart = (weeks) =>
  API.get("/dashboard/charts/po-forecast-vs-actual", { params: { weeks } });
export const getShipmentStagesChart = () => API.get("/dashboard/charts/shipment-stages");
export const getLeadTimePerformanceChart = () => API.get("/dashboard/charts/lead-time-performance");

// Export
export const exportPOExcel = (stage, status) =>
  API.get("/export/po/excel", { params: { stage, status }, responseType: 'blob' });
export const exportPOPDF = (stage, status) =>
  API.get("/export/po/pdf", { params: { stage, status }, responseType: 'blob' });
export const exportInventoryExcel = () =>
  API.get("/export/inventory/excel", { responseType: 'blob' });
export const exportSalesExcel = (startDate, endDate) =>
  API.get("/export/sales/excel", { params: { start_date: startDate, end_date: endDate }, responseType: 'blob' });

// Settings Bulk Update
export const bulkUpdateSettings = (settings) => API.post("/settings/bulk-update", settings);
