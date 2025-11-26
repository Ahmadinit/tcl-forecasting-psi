import React from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Button
} from "@mui/material";
import { Inventory as InventoryIcon } from "@mui/icons-material";

export default function Navbar({ onLogout }) {
  return (
    <AppBar position="fixed" elevation={2} sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <InventoryIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          PSI Forecast System
        </Typography>
        <Box>
          <Button color="inherit" onClick={onLogout}>
            Logout
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}