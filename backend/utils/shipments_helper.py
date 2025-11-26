from datetime import date, timedelta
from sqlalchemy.orm import Session
from models import PurchaseOrder
from typing import List, Dict

class ShipmentHelper:
    """Helper functions for shipment tracking and management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_delayed_shipments(self) -> List[Dict]:
        """Get shipments that are delayed (ETA passed but not delivered)"""
        today = date.today()
        
        delayed_shipments = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.eta < today,
            PurchaseOrder.status.in_(["ordered", "shipped"]),
            PurchaseOrder.stage != "CBU Warehouse"
        ).all()
        
        result = []
        for shipment in delayed_shipments:
            delay_days = (today - shipment.eta).days
            result.append({
                "po_id": shipment.id,
                "po_number": shipment.po_number,
                "product_id": shipment.product_id,
                "eta": shipment.eta.isoformat() if shipment.eta else None,  # type: ignore
                "current_stage": shipment.stage,
                "delay_days": delay_days,
                "status": shipment.status
            })
        
        return result
    
    def update_shipment_progress(self) -> Dict:
        """Update shipment progress based on scheduled timeline"""
        # This would typically integrate with actual shipping APIs
        # For now, we'll simulate progress updates
        
        shipments = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.status.in_(["ordered", "shipped"])
        ).all()
        
        updated_count = 0
        for shipment in shipments:
            if not shipment.etd or not shipment.eta:  # type: ignore
                continue
            
            days_since_etd = (date.today() - shipment.etd).days  # type: ignore
            total_days = (shipment.eta - shipment.etd).days  # type: ignore
            
            if total_days <= 0:
                continue
            
            progress = min(100, (days_since_etd / total_days) * 100)
            
            # Update stage based on progress
            if progress >= 90 and shipment.stage != "CBU Warehouse":  # type: ignore
                shipment.stage = "CBU Warehouse"  # type: ignore
                shipment.status = "delivered"  # type: ignore
                updated_count += 1
            elif progress >= 70 and shipment.stage not in ["Assembly", "CBU Warehouse"]:  # type: ignore
                shipment.stage = "Assembly"  # type: ignore
                updated_count += 1
            elif progress >= 50 and shipment.stage not in ["Customs Clearance", "Assembly", "CBU Warehouse"]:  # type: ignore
                shipment.stage = "Customs Clearance"  # type: ignore
                updated_count += 1
            elif progress >= 30 and shipment.stage not in ["Shipped", "Customs Clearance", "Assembly", "CBU Warehouse"]:  # type: ignore
                shipment.stage = "Shipped"  # type: ignore
                updated_count += 1
        
        if updated_count > 0:
            self.db.commit()
        
        return {
            "message": f"Updated {updated_count} shipments",
            "updated_count": updated_count
        }
    
    def get_shipment_timeline(self, po_id: int) -> Dict:
        """Get detailed timeline for a shipment"""
        shipment = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if not shipment:
            return {}
        
        stages = [
            "CKD Materials Prepared",
            "Booking Confirmed", 
            "Shipped",
            "Customs Clearance",
            "Assembly",
            "CBU Warehouse"
        ]
        
        timeline = []
        current_stage_index = stages.index(shipment.stage) if shipment.stage in stages else -1  # type: ignore
        
        for i, stage in enumerate(stages):
            status = "completed" if i < current_stage_index else "current" if i == current_stage_index else "pending"
            timeline.append({
                "stage": stage,
                "status": status,
                "order": i + 1
            })
        
        return {
            "po_id": shipment.id,
            "po_number": shipment.po_number,
            "current_stage": shipment.stage,
            "progress_percentage": round(((current_stage_index + 1) / len(stages)) * 100),
            "timeline": timeline,
            "etd": shipment.etd.isoformat() if shipment.etd else None,  # type: ignore
            "eta": shipment.eta.isoformat() if shipment.eta else None,  # type: ignore
            "days_until_eta": (shipment.eta - date.today()).days if shipment.eta else None  # type: ignore
        }

def get_shipment_helper(db: Session) -> ShipmentHelper:
    """Dependency injection for shipment helper"""
    return ShipmentHelper(db)