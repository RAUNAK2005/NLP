import csv
import json
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.db.models import Comparison


def comparison_to_dict(comparison: Comparison) -> dict[str, Any]:
    return {
        "id": comparison.id,
        "created_at": comparison.created_at.isoformat(),
        "scores": {
            "overall": comparison.overall_score,
            "fidelity": comparison.fidelity_score,
            "diversity": comparison.diversity_score,
            "utility": comparison.utility_score,
        },
        "configuration": comparison.configuration,
        "interpretation": comparison.interpretation,
        "metrics": [
            {
                "metric_name": metric.metric_name,
                "original_value": metric.original_value,
                "synthetic_value": metric.synthetic_value,
                "absolute_difference": metric.absolute_difference,
                "relative_difference": metric.relative_difference,
                "similarity_score": metric.similarity_score,
                "category": metric.category,
                "direction": metric.direction,
                "interpretation": metric.interpretation,
            }
            for metric in comparison.metrics
        ],
        "payload": comparison.payload,
    }


def json_report(comparison: Comparison) -> str:
    return json.dumps(comparison_to_dict(comparison), indent=2)


def csv_report(comparison: Comparison) -> str:
    buffer = StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "metric_name",
            "original_value",
            "synthetic_value",
            "absolute_difference",
            "relative_difference",
            "similarity_score",
            "category",
            "direction",
            "interpretation",
        ],
    )
    writer.writeheader()
    for metric in comparison.metrics:
        writer.writerow(
            {
                "metric_name": metric.metric_name,
                "original_value": metric.original_value,
                "synthetic_value": metric.synthetic_value,
                "absolute_difference": metric.absolute_difference,
                "relative_difference": metric.relative_difference,
                "similarity_score": metric.similarity_score,
                "category": metric.category,
                "direction": metric.direction,
                "interpretation": metric.interpretation,
            }
        )
    return buffer.getvalue()


def pdf_report_path(comparison: Comparison) -> Path:
    temp = NamedTemporaryFile(delete=False, suffix=f"-comparison-{comparison.id}.pdf")
    temp.close()
    path = Path(temp.name)
    styles = getSampleStyleSheet()
    document = SimpleDocTemplate(str(path), pagesize=letter)
    rows = [["Metric", "Original", "Synthetic", "Similarity"]]
    for metric in comparison.metrics:
        rows.append(
            [
                metric.metric_name,
                "" if metric.original_value is None else f"{metric.original_value:.4g}",
                "" if metric.synthetic_value is None else f"{metric.synthetic_value:.4g}",
                "" if metric.similarity_score is None else f"{metric.similarity_score:.2%}",
            ]
        )
    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ]
        )
    )
    story = [
        Paragraph("Synthetic Dataset Evaluation Report", styles["Title"]),
        Paragraph(f"Overall Score: {comparison.overall_score:.1f}/100", styles["Heading2"]),
        Paragraph(comparison.interpretation, styles["BodyText"]),
        Spacer(1, 16),
        Paragraph("Project-Defined Composite Score", styles["Heading2"]),
        Paragraph(
            "This score combines fidelity, diversity, and downstream utility. It is designed for this project and should not be treated as a universal scientific standard.",
            styles["BodyText"],
        ),
        Spacer(1, 16),
        table,
    ]
    document.build(story)
    return path

