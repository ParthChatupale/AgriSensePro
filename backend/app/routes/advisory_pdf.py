"""
PDF Generator for Advisory Reports
Generates beautiful, structured PDF reports for crop advisories.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from io import BytesIO
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import sys
import os

# Add backend directory to path for imports
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, BACKEND_DIR)

# Import advisory generation logic
from app.fusion_engine import (
    resolve_weather_context,
    fetch_ndvi_context,
    fetch_market_price,
    load_crop_mock,
    build_advisory_from_features,
    generate_advisory,
    compute_ndvi_change,
)

router = APIRouter(prefix="/advisory", tags=["Advisory PDF"])


def format_date(date_string: Optional[str]) -> str:
    """Format date string for display."""
    if not date_string or date_string == "recently":
        return "Recently"
    try:
        # Try to parse ISO format or other common formats
        if isinstance(date_string, str):
            # Handle various date formats
            if "T" in date_string:
                date_obj = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
            else:
                date_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            return date_obj.strftime("%B %d, %Y at %I:%M %p")
    except:
        pass
    return str(date_string)


@router.get("/pdf/{crop_name}")
async def generate_advisory_pdf(
    crop_name: str,
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    village: Optional[str] = None,
):
    """
    Generate a beautiful PDF report for crop advisory.
    Fetches advisory data using existing logic and formats it as PDF.
    """
    try:
        # Fetch advisory data using existing internal logic (same as get_advisory endpoint)
        crop = crop_name.lower()
        weather, geo_info, lat, lon = await resolve_weather_context(
            location=location,
            latitude=latitude,
            longitude=longitude,
            state=state,
            district=district,
            village=village,
        )
        ndvi_latest, ndvi_change, ndvi_history = await fetch_ndvi_context(lat, lon, crop)
        user_context = {
            "user_district": geo_info.get("district"),
            "district": geo_info.get("district"),
            "state": geo_info.get("state"),
            "location": weather.get("location"),
            "ndvi": ndvi_latest,
            "ndvi_change": ndvi_change,
        }

        # Fetch real market price
        market = await fetch_market_price(crop, geo_info.get("district"))
        
        # Check for mock data
        mock = load_crop_mock(crop)
        if mock:
            features = {
                "temperature": weather.get("temperature"),
                "humidity": weather.get("humidity"),
                "rainfall": weather.get("rainfall"),
                "wind_speed": weather.get("wind_speed"),
                "ndvi": ndvi_latest if ndvi_latest is not None else mock.get("ndvi"),
                "soil_moisture": mock.get("soil_moisture"),
                "crop_stage": mock.get("crop_stage", "unknown"),
                "price_change_percent": market.get("price_change_percent", 0),
                "market_price": market.get("price") or mock.get("market_price"),
                "days_since_sowing": mock.get("days_since_sowing"),
                "previous_ndvi": mock.get("previous_ndvi") or mock.get("ndvi_previous"),
                "ndvi_change": (
                    ndvi_change
                    if ndvi_change is not None
                    else compute_ndvi_change(
                        ndvi_latest,
                        mock.get("previous_ndvi") or mock.get("ndvi_previous")
                    )
                ),
                "user_district": mock.get("district") or geo_info.get("district"),
                "district": mock.get("district") or geo_info.get("district"),
            }

            fields, score, fired_rules, breakdown = build_advisory_from_features(crop, features, user_context)
            legacy_priority = "High" if score >= 0.8 else ("Medium" if score >= 0.6 else "Low")
            advisory_data = {
                "crop": crop.capitalize(),
                "analysis": fields["summary"],
                "priority": legacy_priority,
                "severity": fields["severity"].capitalize(),
                "rule_score": score,
                "fired_rules": fired_rules,
                "recommendations": [],
                "rule_breakdown": breakdown,
                "data_sources": {"weather": "Open-Meteo", "satellite": "Bhuvan", "market": "Agmarknet"},
                "last_updated": weather.get("timestamp", "recently"),
                "summary": fields["summary"],
                "alerts": fields["alerts"],
                "metrics": fields["metrics"],
            }
            if advisory_data.get("metrics") is not None and ndvi_history:
                advisory_data["metrics"]["ndvi_history"] = ndvi_history
        else:
            # Use generate_advisory for non-mock crops
            advisory_data = await generate_advisory(
                crop,
                weather,
                user_context,
                ndvi_latest=ndvi_latest,
                ndvi_change=ndvi_change,
                ndvi_history=ndvi_history,
            )
            if ndvi_history and isinstance(advisory_data.get("metrics"), dict):
                advisory_data["metrics"]["ndvi_history"] = ndvi_history
        
        # Generate PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for PDF content
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Title style (Blue)
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0D6EFD'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Section header style (Green)
        section_style = ParagraphStyle(
            'CustomSection',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#198754'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14
        )
        
        # Card style for recommendations
        card_style = ParagraphStyle(
            'CardStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=8,
            leftIndent=12,
            rightIndent=12,
            backColor=colors.HexColor('#F0F8FF'),
            borderPadding=8
        )
        
        # Footer style (Italic)
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
        
        # Build PDF content
        
        # Title
        crop_name_display = advisory_data.get('crop', crop_name.capitalize())
        title_text = f"Crop Advisory Report: {crop_name_display}"
        story.append(Paragraph(title_text, title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Priority and Severity badges
        priority = advisory_data.get('priority', 'N/A')
        severity = advisory_data.get('severity', 'N/A')
        priority_text = f"<b>Priority:</b> {priority} | <b>Severity:</b> {severity}"
        story.append(Paragraph(priority_text, normal_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Last Updated
        last_updated = format_date(advisory_data.get('last_updated'))
        confidence = advisory_data.get('rule_score', 0)
        confidence_percent = int(confidence * 100) if confidence else 0
        date_text = f"<b>Last Updated:</b> {last_updated}"
        if confidence_percent > 0:
            date_text += f" | <b>Confidence:</b> {confidence_percent}%"
        story.append(Paragraph(date_text, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Analysis Section
        story.append(Paragraph("Analysis", section_style))
        analysis = advisory_data.get('analysis', advisory_data.get('summary', 'No analysis available.'))
        story.append(Paragraph(analysis, normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Recommendations Section
        recommendations = advisory_data.get('recommendations', [])
        if recommendations and len(recommendations) > 0:
            story.append(Paragraph("Recommended Actions", section_style))
            
            for idx, rec in enumerate(recommendations, 1):
                rec_title = rec.get('title', f'Recommendation {idx}')
                rec_desc = rec.get('desc', rec.get('description', ''))
                rec_priority = rec.get('priority', 'Medium')
                rec_timeline = rec.get('timeline', '')
                
                # Create recommendation card
                rec_text = f"<b>{rec_title}</b>"
                if rec_priority:
                    rec_text += f" <i>({rec_priority} Priority)</i>"
                rec_text += f"<br/>{rec_desc}"
                if rec_timeline:
                    rec_text += f"<br/><i>Timeline: {rec_timeline}</i>"
                
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(rec_text, card_style))
                story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("Recommended Actions", section_style))
            story.append(Paragraph("No specific recommendations available at this time.", normal_style))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Rule Breakdown Table
        rule_breakdown = advisory_data.get('rule_breakdown', {})
        if rule_breakdown:
            story.append(Paragraph("Rule Breakdown", section_style))
            
            # Prepare table data
            table_data = [['Category', 'Score', 'Rules Triggered']]
            
            for category in ['pest', 'irrigation', 'market']:
                cat_data = rule_breakdown.get(category, {})
                score = cat_data.get('score', 0)
                fired = cat_data.get('fired', [])
                fired_count = len(fired) if isinstance(fired, list) else 0
                score_percent = int(score * 100) if score else 0
                
                category_name = category.capitalize()
                table_data.append([
                    category_name,
                    f"{score_percent}%",
                    str(fired_count)
                ])
            
            # Create table
            table = Table(table_data, colWidths=[2*inch, 1.5*inch, 2*inch])
            table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D6EFD')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                # Data rows
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
        
        # Fired Rules (if available)
        fired_rules = advisory_data.get('fired_rules', [])
        if fired_rules and len(fired_rules) > 0:
            story.append(Paragraph("Triggered Rules", section_style))
            rules_text = "<br/>".join([f"• {rule}" for rule in fired_rules[:10]])  # Limit to 10 rules
            if len(fired_rules) > 10:
                rules_text += f"<br/>... and {len(fired_rules) - 10} more"
            story.append(Paragraph(rules_text, normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer_text = "Generated by krushiRakshak AI"
        story.append(Paragraph(footer_text, footer_style))
        story.append(Spacer(1, 0.1*inch))
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"Report generated on {timestamp}", footer_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        buffer.seek(0)
        pdf_bytes = buffer.read()
        buffer.close()
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="Advisory_{crop_name.capitalize()}.pdf"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF: {str(e)}"
        )

