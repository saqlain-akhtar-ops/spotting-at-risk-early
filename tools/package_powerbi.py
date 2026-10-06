"""Build a reviewable Power BI delivery without replacing the user's old CSVs."""
from pathlib import Path
import csv, hashlib, json, re, shutil, zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/PowerBI_AtRisk_2026-10-06'
DEST=Path('C:/Users/91731/OneDrive/Desktop/Dummy_hackathon/files/PowerBI_AtRisk_2026-10-06')
OUT.mkdir(parents=True,exist_ok=True)
for folder in ['csv','powerquery','model-draft','measures']: (OUT/folder).mkdir(exist_ok=True)
for source in (ROOT/'analytics/export').glob('*'):shutil.copy2(source,OUT/'csv'/source.name)
old=str((ROOT/'analytics/export').resolve()).replace('\\','/')
new=str(DEST/'csv').replace('\\','/')
for source in (ROOT/'analytics/powerquery').glob('*.pq'):(OUT/'powerquery'/source.name).write_text(source.read_text(encoding='utf-8').replace(old,new),encoding='utf-8')
for source in (ROOT/'analytics/model-draft').rglob('*'):
    if source.is_file():
        target=OUT/'model-draft'/source.relative_to(ROOT/'analytics/model-draft');target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(source.read_text(encoding='utf-8').replace(old,new),encoding='utf-8')
names=[]
for filename in ['measures.dax','additional-measures.dax']:
    text=(ROOT/'analytics'/filename).read_text(encoding='utf-8');(OUT/filename).write_text(text,encoding='utf-8')
    chunks=re.findall(r'MEASURE (\w+)\[([^\]]+)\]\s*=\s*(.*?)(?=\n\s*MEASURE |\nEVALUATE|\Z)',text,re.S)
    for table,name,expression in chunks:
        (OUT/'measures'/(name+'.dax')).write_text(name+' =\n'+expression.strip()+'\n',encoding='utf-8')
        names.append({'table':table,'measure':name,'format':'Percentage' if any(x in name for x in ['Rate','Share','Coverage']) else 'Text' if name in ['Status Color','Trend Label','Current Student Status'] else 'Whole number' if any(x in name for x in ['Students','Learners','Performers','Reports','Assigned','Attended','Pending','Count','Term']) else 'Decimal 0.0'})
with (OUT/'measure-catalog.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=['table','measure','format']);writer.writeheader();writer.writerows(names)
for filename in ['rls.dax','LiveDemo.pq','theme.json','data-contract.json','POWER-BI.md']:shutil.copy2(ROOT/'analytics'/filename,OUT/filename)
for filename in ['LIVE-DEMO.md','REACT-DASHBOARD.md']:shutil.copy2(ROOT/'docs'/filename,OUT/filename)
(OUT/'START-HERE.md').write_text('''# Power BI project files — TEAM BLACKCATS

These files use the current synthetic database. The old files in the parent folder are preserved. This is a source/data package, not a tested PBIX report.

1. Open Power BI Desktop. For each file in powerquery, create a Blank Query, paste its contents in Advanced Editor, and name the query after the file (without .pq). CSV paths already point to this delivery folder.
2. Follow the relationship table in POWER-BI.md. Use single-direction active relationships. Dim_UserAccess stays disconnected.
3. For each file in measures, choose New measure on the table listed in measure-catalog.csv and paste the expression. Set the listed format. Score/attendance are 0–100 numbers, not 0–1 percentages.
4. Import theme.json through View → Themes → Browse for themes.
5. Build the eight report pages described in POWER-BI.md. Use Average Score by Term for the trend axis, Status Count with Fact_Status[status] for the ring, and student-filtered score/attendance for the scatter. Use Status Color as field-value formatting on student rows. Add Student 360 drillthrough, page navigation buttons, tooltips, single-select term/class slicers and Reset bookmarks. Keep subject interactions disabled for stored all-subject status visuals.
6. Configure StudentAccess using rls.dax and test every role. Replace example.test mappings with real user identities before publishing. An unknown user must see no student records.
7. Reconcile row counts with csv/manifest.json. Check latest-term KPI counts against the running backend. Then save your PBIX/PBIP.

Live source option: LiveDemo.pq reads the authenticated local backend instead of the snapshot CSVs. It is a Web Import query and needs a Power BI model refresh. See LIVE-DEMO.md. Credentials remain in Power BI's credential dialog.

The native model-draft includes the original 21 measures. The additional visual measures are supplied separately; add them through New measure. All DAX and native artifacts remain drafts until executed and validated in Power BI Desktop. No Desktop report or Service publishing is claimed.
''',encoding='utf-8')
manifest={str(p.relative_to(OUT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
(OUT/'package-manifest.json').write_text(json.dumps({'synthetic':True,'native_validated':False,'measures':len(names),'files':manifest},indent=2),encoding='utf-8')
archive=ROOT/'deliverables/PowerBI_AtRisk_2026-10-06.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.rglob('*'):
        if p.is_file():z.write(p,str(Path(OUT.name)/p.relative_to(OUT)))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(f'Prepared {len(names)} DAX measures, 10 CSV tables and Power BI code in {OUT}')
