from fastapi import APIRouter, Depends, Response
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.comparison_service import get_comparison
from app.services.report_service import csv_report, json_report, pdf_report_path

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/comparisons/{comparison_id}.json")
def export_json(comparison_id: int, db: Session = Depends(get_db)):
    comparison = get_comparison(db, comparison_id)
    return Response(
        content=json_report(comparison),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="comparison-{comparison_id}.json"'},
    )


@router.get("/comparisons/{comparison_id}.csv")
def export_csv(comparison_id: int, db: Session = Depends(get_db)):
    comparison = get_comparison(db, comparison_id)
    return PlainTextResponse(
        content=csv_report(comparison),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="comparison-{comparison_id}.csv"'},
    )


@router.get("/comparisons/{comparison_id}.pdf")
def export_pdf(comparison_id: int, db: Session = Depends(get_db)):
    comparison = get_comparison(db, comparison_id)
    path = pdf_report_path(comparison)
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"comparison-{comparison_id}.pdf",
    )

