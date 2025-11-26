"""
Export router for Excel and PDF exports
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from database import get_db
from utils.export_excel import ExcelExporter
from utils.export_pdf import export_simple_text
import io

router = APIRouter(
    prefix="/export",
    tags=["export"]
)

# GET: Export Purchase Orders to Excel
@router.get("/po/excel")
def export_po_excel(
    stage: Optional[str] = Query(None, description="Filter by stage: CKD Prepared, Booking, Shipped, Customs, Assembly"),
    status: Optional[str] = Query(None, description="Filter by status: suggested, ordered, shipped, delivered, cancelled"),
    db: Session = Depends(get_db)
):
    """Export purchase orders to Excel format with optional filtering"""
    exporter = ExcelExporter(db)
    excel_file = exporter.export_purchase_orders(stage=stage, status=status)
    
    filename = "purchase_orders.xlsx"
    if stage:
        filename = f"purchase_orders_{stage.lower().replace(' ', '_')}.xlsx"
    
    return StreamingResponse(
        io.BytesIO(excel_file.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# GET: Export Purchase Orders to PDF
@router.get("/po/pdf")
def export_po_pdf(
    stage: Optional[str] = Query(None, description="Filter by stage"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Export purchase orders to PDF format with optional filtering"""
    try:
        from utils.export_pdf import export_simple_text
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="PDF export is not available. Please install reportlab: pip install reportlab"
        )
    
    from models import PurchaseOrder, ProductModel
    from sqlalchemy import and_
    
    query = db.query(PurchaseOrder, ProductModel).join(
        ProductModel, PurchaseOrder.product_id == ProductModel.id
    ).filter(ProductModel.is_active == True)
    
    if stage:
        query = query.filter(PurchaseOrder.stage == stage)
    if status:
        query = query.filter(PurchaseOrder.status == status)
    
    pos = query.order_by(PurchaseOrder.order_week.desc()).all()
    
    # Generate PDF content
    lines = ["Purchase Orders Report", "=" * 50, ""]
    if stage:
        lines.append(f"Filtered by Stage: {stage}")
    if status:
        lines.append(f"Filtered by Status: {status}")
    lines.append("")
    
    for po, product in pos:
        lines.append(f"PO Number: {po.po_number or f'PO-{po.id}'}")
        lines.append(f"Product: {product.sku} - {product.name}")
        lines.append(f"Quantity: {po.quantity}")
        lines.append(f"Order Week: {po.order_week}")
        lines.append(f"Stage: {po.stage}")
        lines.append(f"Status: {po.status}")
        lines.append("-" * 50)
    
    # Create PDF
    pdf_buffer = export_simple_text(
        filename=f"purchase_orders_{stage or 'all'}.pdf",
        title="Purchase Orders Report",
        lines=lines
    )
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=purchase_orders_{stage or 'all'}.pdf"}
    )

# GET: Export Inventory to Excel
@router.get("/inventory/excel")
def export_inventory_excel(db: Session = Depends(get_db)):
    """Export inventory status to Excel"""
    exporter = ExcelExporter(db)
    excel_file = exporter.export_inventory_status()
    
    return StreamingResponse(
        io.BytesIO(excel_file.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=inventory_status.xlsx"}
    )

# GET: Export Sales to Excel
@router.get("/sales/excel")
def export_sales_excel(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db)
):
    """Export sales data to Excel"""
    exporter = ExcelExporter(db)
    excel_file = exporter.export_sales_data(start_date, end_date)
    
    return StreamingResponse(
        io.BytesIO(excel_file.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=sales_{start_date}_{end_date}.xlsx"}
    )

