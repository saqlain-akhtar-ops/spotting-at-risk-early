"""In-memory, branded PDF rendering of a saved report snapshot."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

BLUE = colors.HexColor('#3157D5')
INK = colors.HexColor('#172033')
PALE = colors.HexColor('#F4F1EB')

def render_report_pdf(data, report):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40,
                            topMargin=36, bottomMargin=40, title='Student progress report')
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Brand', fontSize=10, textColor=BLUE, spaceAfter=12))
    styles.add(ParagraphStyle(name='ReportTitle', fontSize=25, leading=29, textColor=INK, spaceAfter=15))
    styles.add(ParagraphStyle(name='Section', fontSize=13, leading=17, textColor=BLUE, spaceBefore=12, spaceAfter=7))
    styles.add(ParagraphStyle(name='Copy', fontSize=9.5, leading=14, textColor=INK, spaceAfter=7, splitLongWords=True))
    styles.add(ParagraphStyle(name='Metric', fontSize=12, leading=18, alignment=TA_CENTER, textColor=INK))
    def p(value, style='Copy'):
        return Paragraph(escape(str(value if value is not None else 'Not available')).replace('\n','<br/>'), styles[style])
    def num(v, suffix=''):
        return 'N/A' if v is None else f'{v:.1f}{suffix}'
    def grid(rows, widths):
        t=Table([[p(v) for v in row] for row in rows], colWidths=widths, repeatRows=1, hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),
            ('LINEBELOW',(0,0),(-1,-1),.5,colors.HexColor('#DED9D0'))]))
        return t
    from datetime import datetime
    generated=datetime.fromisoformat(str(report.generated_at)).strftime('%d %b %Y, %H:%M UTC')
    student=data['student']; term=data['term']; ind=data['indicators']
    story=[p('TEAM BLACKCATS  /  SPOTTING THE AT-RISK EARLY','Brand'),p('Student Progress Report','ReportTitle'),
           p(f"{student['name']} | {student['class_name']} | {term['name']}"),
           p(f"Report #{report.id} | Version {report.version} | {'Released' if report.released else 'Draft'} | {generated}"),
           p('Synthetic demonstration data. Indicators support teacher review; they are not a diagnosis.')]
    metrics=Table([[p('Average score\n'+num(ind.get('current_average'),'%'),'Metric'),
                    p('Attendance\n'+num(ind.get('attendance'),'%'),'Metric'),
                    p('Term change\n'+num(ind.get('trend_delta'))+' points','Metric')]],colWidths=[(A4[0]-80)/3]*3)
    metrics.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('TOPPADDING',(0,0),(-1,-1),14),('BOTTOMPADDING',(0,0),(-1,-1),14)]))
    story += [Spacer(1,12),metrics,p('Academic review','Section'),p('Status: '+ind.get('status','Not available')),
              p('Review signals: '+', '.join(x.replace('_',' ').capitalize() for x in ind.get('reason_codes',[]))),
              p('Subject performance','Section')]
    story.append(grid([['Subject','Score','Previous','Change','Attendance']]+[
        [s['subject'],num(s.get('score'),'%'),num(s.get('previous'),'%'),num(s.get('delta')),num(s.get('attendance'),'%')]
        for s in data.get('subjects',[])],[155,70,70,70,A4[0]-445]))
    story.append(p('Support and practice','Section'))
    support=data.get('support',[])
    if not support:story.append(p('No extra-class enrollment recorded in this snapshot.'))
    for entry in support:
        c=entry.get('class',{})
        story.append(p(f"{c.get('topic','Extra class')} | {c.get('date','Date not recorded')} | Room: {c.get('room','N/A')} | Attendance: {entry.get('attendance','PENDING')}"))
        if entry.get('outcome'):story.append(p('Recorded outcome: '+entry['outcome']))
    story.append(p(f"Assignments in snapshot: {len(data.get('assignments',[]))} | Student submissions: {len(data.get('submissions',[]))}"))
    story += [p('Teacher comments','Section'),p(report.comments or 'No comments recorded.'),
              p('Follow-up plan','Section'),p(report.follow_up or 'No follow-up plan recorded.'),
              p(data.get('note','Support outcomes require subsequent evidence.'))]
    def footer(canvas, doc):
        canvas.saveState();canvas.setStrokeColor(BLUE);canvas.line(40,31,A4[0]-40,31)
        canvas.setFont('Helvetica',8);canvas.setFillColor(INK)
        canvas.drawString(40,19,'TEAM BLACKCATS | Academic support workspace')
        canvas.drawRightString(A4[0]-40,19,f'Page {doc.page}');canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return buffer.getvalue()
