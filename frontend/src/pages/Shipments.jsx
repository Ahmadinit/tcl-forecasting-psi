// frontend/src/pages/Shipments.jsx
import React, { useEffect, useState } from "react";
import { Box, Typography, Paper, TextField, Button } from "@mui/material";
import { listShipments, updateShipmentStage, listPOs } from "../services/api";

export default function Shipments() {
  const [shipments, setShipments] = useState([]);
  const [pos, setPos] = useState([]);
  const [form, setForm] = useState({ purchase_order_id: "", stage: "Booking" });

  useEffect(() => {
    load();
    listPOs().then((r) => setPos(r.data)).catch(() => {});
  }, []);

  const load = () => listShipments().then((r) => setShipments(r.data)).catch(() => setShipments([]));

  const submit = async () => {
    await updateShipmentStage(form);
    setForm({ purchase_order_id: "", stage: "Booking" });
    load();
  };

  return (
    <Box>
      <Typography variant="h4" mb={2}>Shipments</Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6">Update Shipment Stage</Typography>
        <Box className="form-row" sx={{ mt: 2 }}>
          <TextField select label="PO" value={form.purchase_order_id} onChange={(e) => setForm({ ...form, purchase_order_id: +e.target.value })} SelectProps={{ native: true }}>
            <option value="">-- select PO --</option>
            {pos.map((p) => <option key={p.id} value={p.id}>PO#{p.id} - Model {p.model_id}</option>)}
          </TextField>
          <TextField select label="Stage" value={form.stage} onChange={(e) => setForm({ ...form, stage: e.target.value })} SelectProps={{ native: true }}>
            <option value="CKD Prepared">CKD Prepared</option>
            <option value="Booking">Booking</option>
            <option value="Shipped">Shipped</option>
            <option value="Customs">Customs</option>
            <option value="Assembly">Assembly</option>
            <option value="Warehouse">Warehouse</option>
          </TextField>
          <Button variant="contained" onClick={submit}>Update Stage</Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Typography variant="h6">Shipment History</Typography>
        {shipments.length === 0 ? <Typography>No shipments</Typography> : shipments.slice().reverse().map((s) => (
          <Box key={s.id} sx={{ mb: 1 }}>
            <Typography>PO#{s.purchase_order_id} — {s.stage} — {new Date(s.updated_at).toLocaleString()}</Typography>
          </Box>
        ))}
      </Paper>
    </Box>
  );
}
