"""
reports/pdf_generator.py
Generates student progress reports as PDF using ReportLab.
Falls back to a plain HTML response if ReportLab is not installed.
"""
import io
from datetime import date


def generate_student_report(student, grades, attendance_records, notes, cat_attempts):
    """
    Returns a BytesIO PDF buffer with the full student progress report.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm, cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, KeepTogether
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        return None   # caller will fall back to HTML

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
        title=f"Progress Report – {student.full_name}",
    )

    # ── Colours ──────────────────────────────────────────
    DARK    = colors.HexColor('#0a0d14')
    ACCENT  = colors.HexColor('#00f5d4')
    PURPLE  = colors.HexColor('#7c3aed')
    GREEN   = colors.HexColor('#10b981')
    RED     = colors.HexColor('#ef4444')
    AMBER   = colors.HexColor('#f59e0b')
    LIGHT   = colors.HexColor('#f8f9fa')
    MUTED   = colors.HexColor('#6b7280')
    WHITE   = colors.white

    # ── Styles ────────────────────────────────────────────
    styles = getSampleStyleSheet()
    h1  = ParagraphStyle('h1',  fontSize=22, textColor=DARK,   spaceAfter=4,  fontName='Helvetica-Bold',  alignment=TA_CENTER)
    h2  = ParagraphStyle('h2',  fontSize=14, textColor=PURPLE, spaceAfter=6,  fontName='Helvetica-Bold',  spaceBefore=14)
    sub = ParagraphStyle('sub', fontSize=10, textColor=MUTED,  spaceAfter=12, fontName='Helvetica',       alignment=TA_CENTER)
    body= ParagraphStyle('body',fontSize=10, textColor=DARK,   spaceAfter=4,  fontName='Helvetica',       leading=16)
    sml = ParagraphStyle('sml', fontSize=8,  textColor=MUTED,  fontName='Helvetica')

    elements = []

    # ── Header ────────────────────────────────────────────
    elements.append(Paragraph("KITI ICT DEPARTMENT", h1))
    elements.append(Paragraph("Student Progress Report", sub))
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=12))

    # ── Student info ──────────────────────────────────────
    profile = getattr(student, 'student_profile', None)
    reg_no  = profile.reg_number if profile else 'N/A'
    course  = profile.course     if profile else 'Diploma ICT'
    year    = f"Year {profile.year}" if profile else ''

    info_data = [
        ['Full Name',    student.full_name,  'Reg Number', reg_no],
        ['Email',        student.email,       'Course',     course],
        ['Report Date',  date.today().strftime('%d %B %Y'), 'Year', year],
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 7*cm, 3.5*cm, 5.5*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME',  (0,0),(-1,-1), 'Helvetica'),
        ('FONTNAME',  (0,0),(0,-1),  'Helvetica-Bold'),
        ('FONTNAME',  (2,0),(2,-1),  'Helvetica-Bold'),
        ('FONTSIZE',  (0,0),(-1,-1), 9),
        ('TEXTCOLOR', (0,0),(0,-1),  MUTED),
        ('TEXTCOLOR', (2,0),(2,-1),  MUTED),
        ('ROWBACKGROUNDS', (0,0),(-1,-1), [LIGHT, WHITE]),
        ('GRID',      (0,0),(-1,-1), 0.3, colors.HexColor('#e2e8f0')),
        ('PADDING',   (0,0),(-1,-1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 12))

    # ── Summary stats ─────────────────────────────────────
    valid_grades = [g for g in grades if g.marks_obtained is not None]
    avg_pct  = 0
    if valid_grades:
        avg_pct = round(sum(g.marks_obtained / g.assignment.max_marks * 100 for g in valid_grades) / len(valid_grades))

    att_total   = len(attendance_records)
    att_present = sum(1 for a in attendance_records if a.status in ('present', 'late'))
    att_rate    = round(att_present / att_total * 100) if att_total else 0

    def grade_letter(pct):
        if pct >= 80: return 'A'
        if pct >= 65: return 'B'
        if pct >= 50: return 'C'
        if pct >= 40: return 'D'
        return 'F'

    def grade_color(pct):
        if pct >= 70: return GREEN
        if pct >= 50: return AMBER
        return RED

    elements.append(Paragraph("Summary", h2))
    summary_data = [
        ['Average Grade', 'Attendance Rate', 'Assignments\nSubmitted', 'CATs\nCompleted'],
        [
            f"{avg_pct}%  ({grade_letter(avg_pct)})",
            f"{att_rate}%",
            f"{len(valid_grades)}",
            f"{sum(1 for a in cat_attempts if a.is_complete)}",
        ]
    ]
    summ_table = Table(summary_data, colWidths=[4.5*cm]*4)
    summ_table.setStyle(TableStyle([
        ('FONTNAME',    (0,0),(-1,0),  'Helvetica-Bold'),
        ('FONTNAME',    (0,1),(-1,1),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,0),(-1,0),  9),
        ('FONTSIZE',    (0,1),(-1,1),  18),
        ('TEXTCOLOR',   (0,0),(-1,0),  WHITE),
        ('TEXTCOLOR',   (0,1),(0,1),   grade_color(avg_pct)),
        ('TEXTCOLOR',   (1,1),(1,1),   grade_color(att_rate)),
        ('TEXTCOLOR',   (2,1),(2,1),   PURPLE),
        ('TEXTCOLOR',   (3,1),(3,1),   PURPLE),
        ('BACKGROUND',  (0,0),(-1,0),  DARK),
        ('ALIGN',       (0,0),(-1,-1), 'CENTER'),
        ('VALIGN',      (0,0),(-1,-1), 'MIDDLE'),
        ('GRID',        (0,0),(-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING',     (0,0),(-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1),(-1,-1), [LIGHT]),
    ]))
    elements.append(summ_table)
    elements.append(Spacer(1, 12))

    # ── Assignments & Grades ──────────────────────────────
    elements.append(Paragraph("Assignment Grades", h2))
    if valid_grades:
        grade_data = [['Assignment', 'Subject', 'Score', 'Out of', 'Percentage', 'Grade', 'Feedback']]
        for sub in valid_grades:
            pct = round(sub.marks_obtained / sub.assignment.max_marks * 100)
            grade_data.append([
                Paragraph(sub.assignment.title, sml),
                sub.assignment.subject,
                str(sub.marks_obtained),
                str(sub.assignment.max_marks),
                f"{pct}%",
                grade_letter(pct),
                Paragraph(sub.feedback[:60] if sub.feedback else '—', sml),
            ])
        g_table = Table(grade_data, colWidths=[4.5*cm, 2.5*cm, 1.2*cm, 1.2*cm, 2*cm, 1.2*cm, 5.4*cm])
        g_table.setStyle(TableStyle([
            ('FONTNAME',   (0,0),(-1,0),  'Helvetica-Bold'),
            ('FONTSIZE',   (0,0),(-1,-1), 8),
            ('TEXTCOLOR',  (0,0),(-1,0),  WHITE),
            ('BACKGROUND', (0,0),(-1,0),  DARK),
            ('ROWBACKGROUNDS', (0,1),(-1,-1), [WHITE, LIGHT]),
            ('GRID',       (0,0),(-1,-1), 0.3, colors.HexColor('#e2e8f0')),
            ('PADDING',    (0,0),(-1,-1), 5),
            ('ALIGN',      (2,0),(5,-1),  'CENTER'),
        ]))
        elements.append(g_table)
    else:
        elements.append(Paragraph("No graded assignments yet.", body))
    elements.append(Spacer(1, 8))

    # ── Attendance ────────────────────────────────────────
    elements.append(Paragraph("Attendance Record", h2))
    att_data = [['Date', 'Status']]
    for rec in sorted(attendance_records, key=lambda x: x.date, reverse=True)[:20]:
        att_data.append([
            rec.date.strftime('%d %b %Y'),
            rec.status.capitalize(),
        ])
    if len(att_data) > 1:
        a_table = Table(att_data, colWidths=[5*cm, 5*cm])
        a_table.setStyle(TableStyle([
            ('FONTNAME',   (0,0),(-1,0),  'Helvetica-Bold'),
            ('FONTSIZE',   (0,0),(-1,-1), 9),
            ('TEXTCOLOR',  (0,0),(-1,0),  WHITE),
            ('BACKGROUND', (0,0),(-1,0),  DARK),
            ('ROWBACKGROUNDS', (0,1),(-1,-1), [WHITE, LIGHT]),
            ('GRID',       (0,0),(-1,-1), 0.3, colors.HexColor('#e2e8f0')),
            ('PADDING',    (0,0),(-1,-1), 5),
        ]))
        elements.append(a_table)
        if att_total > 20:
            elements.append(Paragraph(f"Showing last 20 of {att_total} records.", sml))
    else:
        elements.append(Paragraph("No attendance records.", body))
    elements.append(Spacer(1, 8))

    # ── CAT Results ───────────────────────────────────────
    completed_cats = [a for a in cat_attempts if a.is_complete]
    if completed_cats:
        elements.append(Paragraph("CAT Results", h2))
        cat_data = [['CAT Title', 'Subject', 'Score', 'Percentage', 'Date']]
        for attempt in completed_cats:
            pct = attempt.percentage or 0
            cat_data.append([
                Paragraph(attempt.cat.title, sml),
                attempt.cat.subject,
                f"{attempt.score}/{attempt.cat.question_count}",
                f"{pct}%",
                attempt.submitted_at.strftime('%d %b %Y') if attempt.submitted_at else '—',
            ])
        c_table = Table(cat_data, colWidths=[6*cm, 3*cm, 2*cm, 2.5*cm, 4*cm])
        c_table.setStyle(TableStyle([
            ('FONTNAME',   (0,0),(-1,0),  'Helvetica-Bold'),
            ('FONTSIZE',   (0,0),(-1,-1), 8),
            ('TEXTCOLOR',  (0,0),(-1,0),  WHITE),
            ('BACKGROUND', (0,0),(-1,0),  DARK),
            ('ROWBACKGROUNDS', (0,1),(-1,-1), [WHITE, LIGHT]),
            ('GRID',       (0,0),(-1,-1), 0.3, colors.HexColor('#e2e8f0')),
            ('PADDING',    (0,0),(-1,-1), 5),
            ('ALIGN',      (2,0),(4,-1),  'CENTER'),
        ]))
        elements.append(c_table)
        elements.append(Spacer(1, 8))

    # ── Lecturer Notes ────────────────────────────────────
    if notes:
        elements.append(Paragraph("Lecturer Notes", h2))
        for note in notes[:10]:
            type_labels = {
                'note': 'Note', 'feedback': 'Feedback',
                'commendation': '⭐ Commendation', 'warning': '⚠ Warning',
                'instruction': 'Instructions',
            }
            label = type_labels.get(note.type, 'Note')
            note_color = GREEN if note.type == 'commendation' else RED if note.type == 'warning' else DARK
            note_data = [[
                Paragraph(f"<b>{label}</b> — {note.author.full_name}  |  {note.created_at.strftime('%d %b %Y')}", sml),
            ],[
                Paragraph(note.content, body),
            ]]
            n_table = Table(note_data, colWidths=[17.5*cm])
            n_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0),(0,0), LIGHT),
                ('BACKGROUND', (0,1),(0,1), WHITE),
                ('LEFTPADDING',(0,0),(-1,-1), 10),
                ('PADDING',    (0,0),(-1,-1), 6),
                ('GRID',       (0,0),(-1,-1), 0.3, colors.HexColor('#e2e8f0')),
                ('LEFTPADDING',(0,0),(0,0),   8),
                ('LINEBEFORE', (0,0),(0,-1), 3, note_color),
            ]))
            elements.append(n_table)
            elements.append(Spacer(1, 4))

    # ── Footer ────────────────────────────────────────────
    elements.append(Spacer(1, 16))
    elements.append(HRFlowable(width="100%", thickness=1, color=MUTED))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        f"Generated on {date.today().strftime('%d %B %Y')} · KITI ICT Department · Confidential",
        ParagraphStyle('footer', fontSize=8, textColor=MUTED, alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
