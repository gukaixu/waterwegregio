import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

def parse_score(score_text):
    """Convert score text to numeric value - extract first digit (1-5)"""
    if pd.isna(score_text):
        return None
    
    score_text = str(score_text).strip()
    
    # Find the first digit in the text
    for char in score_text:
        if char.isdigit():
            digit = int(char)
            # Only return valid scores 1-5
            if 1 <= digit <= 5:
                return digit
            break
    
    # Fallback to original logic if no digit found
    score_lower = score_text.lower()
    if 'afwezig' in score_lower:
        return 1
    elif 'zwak' in score_lower:
        return 2
    elif 'gedeeltelijk' in score_lower:
        return 3
    elif 'aanwezig' in score_lower and 'sterk' not in score_lower:
        return 4
    elif 'sterk' in score_lower:
        return 5
    
    # Try to parse as float
    try:
        val = float(score_text)
        if 1 <= val <= 5:
            return val
        return None
    except:
        return None

def get_score_background_color(score):
    """Return subtle background color based on score value - simplified 3-color scheme"""
    if score is None:
        return colors.white
    elif score >= 4:
        return colors.HexColor('#e8f5e8')  # Subtle green (4-5)
    elif score >= 3:
        return colors.HexColor('#fff3e0')  # Subtle orange (3-4)
    else:
        return colors.HexColor('#ffebee')  # Subtle red (1-3)

def get_score_color(score):
    """Return color based on score value"""
    if score is None:
        return colors.black
    if score >= 4.5:
        return colors.darkgreen
    elif score >= 3.5:
        return colors.green
    elif score >= 2.5:
        return colors.orange
    elif score >= 1.5:
        return colors.red
    else:
        return colors.darkred

def analyze_excel_file(filename):
    """Analyze a single Excel file and extract project scores"""
    df = pd.read_excel(filename, header=None)
    
    # Project information (row 1, columns C onward)
    projects = {}
    project_cols = range(2, 12)  # Columns C through L (0-indexed: 2-11)
    
    for col in project_cols:
        if col < df.shape[1]:
            project_num = df.iloc[0, col] if col < df.shape[1] else f"Project {col-1}"
            project_title = df.iloc[1, col] if col < df.shape[1] else ""
            
            # Skip if no project title
            if pd.isna(project_title) or str(project_title).strip() == '':
                continue
                
            # Define pillar rows with proper category names
            pillar_definitions = {
                "Impact": {
                    "rows": [3, 4, 5],
                    "categories": ["Impact brede welvaart", "Impact op bewoners", "Innovatie binnen gemeenten"]
                },
                "Regionale inbedding": {
                    "rows": [7, 8, 9],
                    "categories": ["Regiobreedte", "Samenwerkingsbreedte", "Schaalbaarheid"]
                },
                "Financiële verantwoording": {
                    "rows": [11, 12, 13],
                    "categories": ["Doelmatigheid", "Mate van (financiële) inbreng", "Duurzaamheid"]
                },
                "Haalbaarheid": {
                    "rows": [15, 16, 17],
                    "categories": ["Tijdige realisatie", "Projectorganisatie", "Risico's en beheersmaatregelen"]
                }
            }
            
            project_data = {
                'number': project_num,
                'title': project_title,
                'pillars': {}
            }
            
            total_score = 0
            total_categories = 0
            
            for pillar_name, pillar_info in pillar_definitions.items():
                pillar_scores = []
                pillar_details = []
                
                for i, row in enumerate(pillar_info["rows"]):
                    if row < df.shape[0] and col < df.shape[1]:
                        category = pillar_info["categories"][i] if i < len(pillar_info["categories"]) else f"Category {i+1}"
                        score_text = df.iloc[row, col]
                        score = parse_score(score_text)
                        
                        if score is not None:
                            pillar_scores.append(score)
                            total_score += score
                            total_categories += 1
                        
                        pillar_details.append({
                            'category': category,
                            'score': score,
                            'original': score_text
                        })
                
                pillar_avg = np.mean(pillar_scores) if pillar_scores else None
                project_data['pillars'][pillar_name] = {
                    'average': pillar_avg,
                    'details': pillar_details
                }
            
            project_data['total_score'] = total_score / total_categories if total_categories > 0 else None
            projects[f"project_{col-1}"] = project_data
    
    return projects

def create_score_cell(score, is_total=False, is_pillar=False):
    """Create a formatted score cell with color coding"""
    if score is None or score == 0 or pd.isna(score):
        return "-"
    
    score_text = f"{score:.1f}"
    if is_total:
        return score_text
    elif is_pillar:
        return score_text
    else:
        return f"{score:.0f}"

def create_overview_page(all_projects, styles):
    """Create the overview page with all projects and main criteria"""
    overview_elements = []
    
    # Overview title
    title_style = ParagraphStyle(
        'OverviewTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f4e79'),
        fontName='Helvetica-Bold'
    )
    
    overview_elements.append(Paragraph("Overzicht Alle Projecten", title_style))
    overview_elements.append(Spacer(1, 20))
    
    # Create overview table
    overview_data = [
        [
            Paragraph("<b>Project</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10)),
            Paragraph("<b>Impact</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER)),
            Paragraph("<b>Regionale<br/>inbedding</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER)),
            Paragraph("<b>Financiële<br/>verantwoording</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER)),
            Paragraph("<b>Haalbaarheid</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER)),
            Paragraph("<b>Totaalscore</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER))
        ]
    ]
    
    # Add each project as a row
    for proj_key, proj_summary in all_projects.items():
        if not proj_summary['title'] or str(proj_summary['title']).lower() == 'nan':
            continue
            
        # Calculate averages for each pillar
        impact_scores = [s for s in proj_summary['pillar_scores']['Impact'] if s is not None]
        regional_scores = [s for s in proj_summary['pillar_scores']['Regionale inbedding'] if s is not None]
        financial_scores = [s for s in proj_summary['pillar_scores']['Financiële verantwoording'] if s is not None]
        feasibility_scores = [s for s in proj_summary['pillar_scores']['Haalbaarheid'] if s is not None]
        total_scores = [s for s in proj_summary['scores'] if s is not None]
        
        impact_avg = np.mean(impact_scores) if impact_scores else None
        regional_avg = np.mean(regional_scores) if regional_scores else None
        financial_avg = np.mean(financial_scores) if financial_scores else None
        feasibility_avg = np.mean(feasibility_scores) if feasibility_scores else None
        total_avg = np.mean(total_scores) if total_scores else None
        
        # Create project row
        project_row = [
            Paragraph(f"<b>{proj_summary['number']}: {proj_summary['title']}</b>", 
                     ParagraphStyle('ProjectName', fontSize=9, fontName='Helvetica-Bold')),
            Paragraph(f"{impact_avg:.1f}" if impact_avg is not None else "-", 
                     ParagraphStyle('Score', fontSize=9, alignment=TA_CENTER)),
            Paragraph(f"{regional_avg:.1f}" if regional_avg is not None else "-", 
                     ParagraphStyle('Score', fontSize=9, alignment=TA_CENTER)),
            Paragraph(f"{financial_avg:.1f}" if financial_avg is not None else "-", 
                     ParagraphStyle('Score', fontSize=9, alignment=TA_CENTER)),
            Paragraph(f"{feasibility_avg:.1f}" if feasibility_avg is not None else "-", 
                     ParagraphStyle('Score', fontSize=9, alignment=TA_CENTER)),
            Paragraph(f"<b>{total_avg:.1f}</b>" if total_avg is not None else "<b>-</b>", 
                     ParagraphStyle('TotalScore', fontSize=9, alignment=TA_CENTER, fontName='Helvetica-Bold'))
        ]
        
        overview_data.append(project_row)
    
    # Create table
    col_widths = [6*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm]
    overview_table = Table(overview_data, colWidths=col_widths)
    
    # Basic table styling
    table_style = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90d9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
        # General styling
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]
    
    # Add background colors for scores
    row_idx = 1
    for proj_key, proj_summary in all_projects.items():
        if not proj_summary['title'] or str(proj_summary['title']).lower() == 'nan':
            continue
            
        # Calculate averages
        impact_scores = [s for s in proj_summary['pillar_scores']['Impact'] if s is not None]
        regional_scores = [s for s in proj_summary['pillar_scores']['Regionale inbedding'] if s is not None]
        financial_scores = [s for s in proj_summary['pillar_scores']['Financiële verantwoording'] if s is not None]
        feasibility_scores = [s for s in proj_summary['pillar_scores']['Haalbaarheid'] if s is not None]
        total_scores = [s for s in proj_summary['scores'] if s is not None]
        
        averages = [
            np.mean(impact_scores) if impact_scores else None,
            np.mean(regional_scores) if regional_scores else None,
            np.mean(financial_scores) if financial_scores else None,
            np.mean(feasibility_scores) if feasibility_scores else None,
            np.mean(total_scores) if total_scores else None
        ]
        
        # Apply background colors
        for col_idx, avg in enumerate(averages, start=1):
            if avg is not None:
                bg_color = get_score_background_color(avg)
                table_style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), bg_color))
        
        row_idx += 1
    
    overview_table.setStyle(TableStyle(table_style))
    overview_elements.append(overview_table)
    overview_elements.append(PageBreak())
    
    return overview_elements

def create_pdf_summary(all_evaluations, output_filename):
    """Create a modern PDF summary of all evaluations"""
    doc = SimpleDocTemplate(output_filename, pagesize=A4, 
                          topMargin=1*cm, bottomMargin=1*cm, 
                          leftMargin=1.5*cm, rightMargin=1.5*cm)
    
    # Define modern styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ModernTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f4e79'),
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=6,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666'),
        fontName='Helvetica'
    )
    
    subsubtitle_style = ParagraphStyle(
        'SubSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666'),
        fontName='Helvetica'
    )
    
    project_title_style = ParagraphStyle(
        'ProjectTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=8,
        textColor=colors.HexColor('#1f4e79'),
        fontName='Helvetica-Bold'
    )
    
    story = []
    
    # Updated header with new titles
    story.append(Paragraph("Projectevaluatie Samenvatting", title_style))
    story.append(Paragraph("Board Meeting 10 juli 2025", subtitle_style))
    story.append(Paragraph("Regio Deal Waterwegregio", subsubtitle_style))
    story.append(Spacer(1, 30))
    
    # Calculate overall statistics
    all_projects = {}
    for eval_idx, evaluation in enumerate(all_evaluations):
        for proj_key, proj_data in evaluation.items():
            if proj_key not in all_projects:
                all_projects[proj_key] = {
                    'title': proj_data['title'],
                    'number': proj_data['number'],
                    'scores': [],
                    'pillar_scores': {pillar: [] for pillar in proj_data['pillars'].keys()},
                    'detailed_scores': {pillar: {} for pillar in proj_data['pillars'].keys()}
                }
            
            all_projects[proj_key]['scores'].append(proj_data['total_score'])
            for pillar, pillar_data in proj_data['pillars'].items():
                all_projects[proj_key]['pillar_scores'][pillar].append(pillar_data['average'])
                
                # Store detailed category scores
                for detail in pillar_data['details']:
                    cat_name = detail['category']
                    if cat_name not in all_projects[proj_key]['detailed_scores'][pillar]:
                        all_projects[proj_key]['detailed_scores'][pillar][cat_name] = []
                    all_projects[proj_key]['detailed_scores'][pillar][cat_name].append(detail['score'])
    
    # Add overview page first
    overview_elements = create_overview_page(all_projects, styles)
    story.extend(overview_elements)
    
    # Create summary for each project (one page per project)
    project_count = 0
    for proj_key, proj_summary in all_projects.items():
        if not proj_summary['title'] or str(proj_summary['title']).lower() == 'nan':
            continue
            
        project_count += 1
        
        # Calculate average total, excluding None values
        valid_scores = [s for s in proj_summary['scores'] if s is not None]
        avg_total = np.mean(valid_scores) if valid_scores else None
        
        # Project header with score badge - fix duplicate "Project" text
        project_info = f"{proj_summary['number']}: {proj_summary['title']}"
        score_display = f"{avg_total:.1f}/5.0" if avg_total is not None else "-/5.0"
        
        header_data = [
            [
                Paragraph(f"<b>{project_info}</b>", project_title_style),
                Paragraph(f"<b><font size=20>{score_display}</font></b>", 
                         ParagraphStyle('ScoreBadge', alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=colors.HexColor('#1f4e79')))
            ]
        ]
        
        header_table = Table(header_data, colWidths=[13*cm, 5*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1f4e79'))
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # Main scoring table
        table_data = [
            [
                Paragraph("<b>Evaluatiecriteria</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10)),
                Paragraph("<b>Gem.</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER)),
                Paragraph("<b>Eval 1</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER)),
                Paragraph("<b>Eval 2</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER)),
                Paragraph("<b>Eval 3</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER)),
                Paragraph("<b>Eval 4</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER)),
                Paragraph("<b>Eval 5</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER)),
                Paragraph("<b>Eval 6</b>", ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER))
            ]
        ]
        
        pillar_row_indices = [1]  # Track pillar rows for styling
        separator_rows = []  # Track where to add separator lines
        
        for pillar in ['Impact', 'Regionale inbedding', 'Financiële verantwoording', 'Haalbaarheid']:
            pillar_scores = [s for s in proj_summary['pillar_scores'][pillar] if s is not None]
            avg_pillar = np.mean(pillar_scores) if pillar_scores else None
            
            # Add pillar header row
            pillar_row = [
                Paragraph(f"<b>{pillar}</b>", ParagraphStyle('PillarHeader', fontName='Helvetica-Bold', fontSize=11)),
                Paragraph(f"<b>{avg_pillar:.1f}</b>" if avg_pillar is not None else "<b>-</b>", 
                         ParagraphStyle('PillarScore', fontName='Helvetica-Bold', fontSize=11, alignment=TA_CENTER)),
            ]
            for i in range(6):  # Changed to 6 evaluators
                if i < len(proj_summary['pillar_scores'][pillar]):
                    score = proj_summary['pillar_scores'][pillar][i]
                    score_text = f"<b>{score:.1f}</b>" if score is not None else "<b>-</b>"  # Make pillar scores bold
                    pillar_row.append(Paragraph(score_text, 
                                              ParagraphStyle('PillarScore', fontName='Helvetica-Bold', fontSize=11, alignment=TA_CENTER)))
                else:
                    pillar_row.append(Paragraph("<b>-</b>", ParagraphStyle('PillarScore', fontName='Helvetica-Bold', alignment=TA_CENTER)))
            
            table_data.append(pillar_row)
            pillar_row_indices.append(len(table_data) - 1)
            
            # Add subcategory details
            for cat_name, cat_scores in proj_summary['detailed_scores'][pillar].items():
                valid_cat_scores = [s for s in cat_scores if s is not None]
                avg_cat = np.mean(valid_cat_scores) if valid_cat_scores else None
                cat_row = [
                    Paragraph(f"• {cat_name}", ParagraphStyle('SubCategory', fontSize=9, leftIndent=15)),
                    Paragraph(f"{avg_cat:.1f}" if avg_cat is not None else "-", 
                             ParagraphStyle('SubScore', fontSize=9, alignment=TA_CENTER))
                ]
                for i in range(6):  # Changed to 6 evaluators
                    if i < len(cat_scores):
                        score = cat_scores[i]
                        score_text = f"{score:.0f}" if score is not None else "-"
                        cat_row.append(Paragraph(score_text, 
                                               ParagraphStyle('SubScore', fontSize=9, alignment=TA_CENTER)))
                    else:
                        cat_row.append(Paragraph("-", ParagraphStyle('SubScore', fontSize=9, alignment=TA_CENTER)))
                table_data.append(cat_row)
            
            # Mark separator line after each pillar (except the last one)
            if pillar != 'Haalbaarheid':
                separator_rows.append(len(table_data) - 1)
        
        # Add total score row
        total_row = [
            Paragraph("<b>TOTAALSCORE</b>", ParagraphStyle('TotalLabel', fontName='Helvetica-Bold', fontSize=12)),
            Paragraph(f"<b>{avg_total:.1f}</b>" if avg_total is not None else "<b>-</b>", 
                     ParagraphStyle('TotalScore', fontName='Helvetica-Bold', fontSize=12, alignment=TA_CENTER))
        ]
        for i in range(6):  # Changed to 6 evaluators
            if i < len(proj_summary['scores']):
                score = proj_summary['scores'][i]
                score_text = f"{score:.1f}" if score is not None else "-"
                total_row.append(Paragraph(score_text, 
                                         ParagraphStyle('EvalScore', fontSize=12, alignment=TA_CENTER)))
            else:
                total_row.append(Paragraph("-", ParagraphStyle('EvalScore', fontSize=12, alignment=TA_CENTER)))
        table_data.append(total_row)
        
        # Create the table with wider columns for 6 evaluators
        col_widths = [6*cm, 1.6*cm, 1.6*cm, 1.6*cm, 1.6*cm, 1.6*cm, 1.6*cm, 1.6*cm]
        table = Table(table_data, colWidths=col_widths)
        
        # Apply modern styling with lighter blue header and background colors
        table_style = [
            # Header row - lighter blue
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90d9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            
            # Total row - remove blue background
            ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),  # Only bold for label and average
            ('TOPPADDING', (0, -1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
            
            # General styling
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -2), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ]
        
        # Style pillar rows
        for idx in pillar_row_indices:
            if idx < len(table_data):
                table_style.extend([
                    ('BACKGROUND', (0, idx), (-1, idx), colors.HexColor('#f0f8ff')),
                    ('TOPPADDING', (0, idx), (-1, idx), 6),
                    ('BOTTOMPADDING', (0, idx), (-1, idx), 6),
                ])
        
        # Add separator lines between criteria groups
        for sep_row in separator_rows:
            table_style.append(('LINEBELOW', (0, sep_row), (-1, sep_row), 2, colors.HexColor('#1f4e79')))
        
        # Add thick line above TOTAALSCORE row
        table_style.append(('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1f4e79')))
        
        # Add background colors based on scores for average column
        row_idx = 1
        for pillar in ['Impact', 'Regionale inbedding', 'Financiële verantwoording', 'Haalbaarheid']:
            # Pillar average cell
            pillar_scores = [s for s in proj_summary['pillar_scores'][pillar] if s is not None]
            avg_pillar = np.mean(pillar_scores) if pillar_scores else None
            if avg_pillar is not None:
                bg_color = get_score_background_color(avg_pillar)
                table_style.append(('BACKGROUND', (1, row_idx), (1, row_idx), bg_color))
            
            # Individual evaluator cells for pillar
            for col_idx in range(2, 8):  # Eval 1-6 columns
                eval_idx = col_idx - 2
                if eval_idx < len(proj_summary['pillar_scores'][pillar]):
                    score = proj_summary['pillar_scores'][pillar][eval_idx]
                    if score is not None:
                        bg_color = get_score_background_color(score)
                        table_style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), bg_color))
            
            row_idx += 1
            
            # Subcategory rows
            for cat_name in proj_summary['detailed_scores'][pillar].keys():
                cat_scores = proj_summary['detailed_scores'][pillar][cat_name]
                
                # Average cell for subcategory
                valid_cat_scores = [s for s in cat_scores if s is not None]
                avg_cat = np.mean(valid_cat_scores) if valid_cat_scores else None
                if avg_cat is not None:
                    bg_color = get_score_background_color(avg_cat)
                    table_style.append(('BACKGROUND', (1, row_idx), (1, row_idx), bg_color))
                
                # Individual evaluator cells for subcategory
                for col_idx in range(2, 8):  # Eval 1-6 columns
                    eval_idx = col_idx - 2
                    if eval_idx < len(cat_scores):
                        score = cat_scores[eval_idx]
                        if score is not None:
                            bg_color = get_score_background_color(score)
                            table_style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), bg_color))
                
                row_idx += 1
        
        # Add background colors for total score row
        if avg_total is not None:
            bg_color = get_score_background_color(avg_total)
            table_style.append(('BACKGROUND', (1, -1), (1, -1), bg_color))
        
        for col_idx in range(2, 8):  # Total score evaluator columns
            eval_idx = col_idx - 2
            if eval_idx < len(proj_summary['scores']):
                score = proj_summary['scores'][eval_idx]
                if score is not None:
                    bg_color = get_score_background_color(score)
                    table_style.append(('BACKGROUND', (col_idx, -1), (col_idx, -1), bg_color))
        
        table.setStyle(TableStyle(table_style))
        story.append(table)
        
        # Add page break after each project (except the last one)
        if project_count < len([p for p in all_projects.values() if p['title'] and str(p['title']).lower() != 'nan']):
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    print(f"Modern PDF created: {output_filename}")

def main():
    """Main function to process all Excel files and create summary"""
    excel_files = ['excel/1.xlsx', 'excel/2.xlsx', 'excel/3.xlsx', 'excel/4.xlsx', 'excel/5.xlsx', 'excel/6.xlsx']  # Added 6th file
    all_evaluations = []
    
    print("Analyzing Excel files...")
    for i, filename in enumerate(excel_files):
        if os.path.exists(filename):
            print(f"Processing {filename}...")
            try:
                evaluation = analyze_excel_file(filename)
                all_evaluations.append(evaluation)
                print(f"  Found {len(evaluation)} projects in {filename}")
            except Exception as e:
                print(f"  Error processing {filename}: {e}")
        else:
            print(f"Warning: {filename} not found")
    
    if all_evaluations:
        print(f"Creating modern PDF summary for {len(all_evaluations)} evaluation files (6 evaluators)...")
        create_pdf_summary(all_evaluations, "projectevaluatie_overview.pdf")
        print("Modern summary completed!")
    else:
        print("No evaluation files found!")

if __name__ == "__main__":
    main() 