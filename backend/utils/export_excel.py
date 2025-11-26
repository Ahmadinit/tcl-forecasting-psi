import pandas as pd
from datetime import datetime, date
from sqlalchemy.orm import Session
from models import ProductModel, SalesRecord, PurchaseOrder, Inventory
from typing import List, Dict, Optional
import io

class ExcelExporter:
    """Export data to Excel format matching the original Excel templates"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_purchase_forecast(self) -> io.BytesIO:
        """Export purchase forecast data in Excel format"""
        # Get all active products
        products = self.db.query(ProductModel).filter(ProductModel.is_active == True).all()
        
        # Create DataFrame structure matching Excel
        data = []
        for product in products:
            inventory = self.db.query(Inventory).filter(Inventory.product_id == product.id).first()
            current_stock = inventory.current_stock if inventory else 0
            
            data.append({
                'Sales Model': product.sku,
                'Shipping Mode': product.shipping_mode,
                'Status': product.status,
                'Remarks': product.remarks or '',
                'Current Stock': current_stock,
                'Safety Stock Days': product.safety_stock_days
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:  # type: ignore
            df.to_excel(writer, sheet_name='Purchase Forecast', index=False)
            
            # Add formatting similar to original Excel
            workbook = writer.book
            worksheet = writer.sheets['Purchase Forecast']
            
            # Add headers
            for col_num, value in enumerate(df.columns.values):
                from openpyxl.styles import Font  # pyright: ignore[reportMissingModuleSource]
                worksheet.cell(1, col_num + 1).font = Font(bold=True)
        
        output.seek(0)
        return output
    
    def export_sales_data(self, start_date: date, end_date: date) -> io.BytesIO:
        """Export sales data for specified period"""
        sales_data = self.db.query(SalesRecord, ProductModel).join(
            ProductModel, SalesRecord.product_id == ProductModel.id
        ).filter(
            SalesRecord.sale_date >= start_date,
            SalesRecord.sale_date <= end_date
        ).all()
        
        data = []
        for sale, product in sales_data:
            data.append({
                'Date': sale.sale_date.strftime('%Y-%m-%d'),
                'SKU': product.sku,
                'Product Name': product.name,
                'Quantity': sale.quantity,
                'Channel': sale.channel,
                'Created At': sale.created_at.strftime('%Y-%m-%d %H:%M') if sale.created_at else ''
            })
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:  # type: ignore
            df.to_excel(writer, sheet_name='Sales Data', index=False)
        
        output.seek(0)
        return output
    
    def export_psi_report(self, target_month: date) -> io.BytesIO:
        """Export PSI report for a specific month"""
        from .calculations import BusinessCalculations
        
        calculations = BusinessCalculations(self.db)
        products = self.db.query(ProductModel).filter(ProductModel.is_active == True).all()
        
        data = []
        for product in products:
            psi_data = calculations.calculate_monthly_psi(product.id, target_month)  # type: ignore
            if psi_data:
                data.append(psi_data)
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:  # type: ignore
            df.to_excel(writer, sheet_name='PSI Report', index=False)
        
        output.seek(0)
        return output
    
    def export_inventory_status(self) -> io.BytesIO:
        """Export current inventory status"""
        inventory_data = self.db.query(Inventory, ProductModel).join(
            ProductModel, Inventory.product_id == ProductModel.id
        ).filter(ProductModel.is_active == True).all()
        
        data = []
        for inventory, product in inventory_data:
            stock_status = "Low" if inventory.current_stock <= product.safety_stock_days else "Adequate"
            
            data.append({
                'SKU': product.sku,
                'Product Name': product.name,
                'Current Stock': inventory.current_stock,
                'CBU in Hand': inventory.cbu_in_hand,
                'Kits in Factory': inventory.kits_in_factory,
                'Safety Stock Days': product.safety_stock_days,
                'Stock Status': stock_status,
                'Last Updated': inventory.last_updated.strftime('%Y-%m-%d %H:%M') if inventory.last_updated else ''
            })
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:  # type: ignore
            df.to_excel(writer, sheet_name='Inventory Status', index=False)
        
        output.seek(0)
        return output
    
    def export_purchase_orders(self, stage: Optional[str] = None, status: Optional[str] = None) -> io.BytesIO:
        """Export purchase orders with optional filtering by stage or status"""
        from models import PurchaseOrder, ProductModel
        from sqlalchemy import and_
        
        query = self.db.query(PurchaseOrder, ProductModel).join(
            ProductModel, PurchaseOrder.product_id == ProductModel.id
        ).filter(ProductModel.is_active == True)
        
        if stage:
            query = query.filter(PurchaseOrder.stage == stage)
        if status:
            query = query.filter(PurchaseOrder.status == status)
        
        pos = query.order_by(PurchaseOrder.order_week.desc()).all()
        
        data = []
        for po, product in pos:
            data.append({
                'PO Number': po.po_number or f'PO-{po.id}',
                'SKU': product.sku,
                'Product Name': product.name,
                'Quantity': po.quantity,
                'Forecasted Quantity': po.forecasted_quantity or po.quantity,
                'Order Week': po.order_week.strftime('%Y-%m-%d') if po.order_week else '',
                'Order Date': po.order_date.strftime('%Y-%m-%d') if po.order_date else '',
                'Expected Delivery Week': po.expected_delivery_week.strftime('%Y-%m-%d') if po.expected_delivery_week else '',
                'ETD': po.etd.strftime('%Y-%m-%d') if po.etd else '',
                'ETA': po.eta.strftime('%Y-%m-%d') if po.eta else '',
                'Status': po.status,
                'Stage': po.stage or '',
                'Shipping Mode': po.shipping_mode,
                'Notes': po.notes or '',
                'Created At': po.created_at.strftime('%Y-%m-%d %H:%M') if po.created_at else '',
                'Updated At': po.updated_at.strftime('%Y-%m-%d %H:%M') if po.updated_at else ''
            })
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:  # type: ignore
            sheet_name = 'Purchase Orders'
            if stage:
                sheet_name = f'POs - {stage}'
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        output.seek(0)
        return output

def get_excel_exporter(db: Session) -> ExcelExporter:
    """Dependency injection for Excel exporter"""
    return ExcelExporter(db)