"""Prepare reviewable native TMDL source. Desktop validation is still required."""
from pathlib import Path
import csv, re, json, uuid
ROOT=Path(__file__).resolve().parents[1]
model=ROOT/'analytics/model-draft/AtRisk.SemanticModel'
definition=model/'definition'
(definition/'tables').mkdir(parents=True,exist_ok=True)
(definition/'roles').mkdir(exist_ok=True)
(model/'definition.pbism').write_text(json.dumps({'version':'4.0','settings':{}},indent=2),encoding='utf-8')
(definition/'database.tmdl').write_text('database\n\tcompatibilityLevel: 1600\n',encoding='utf-8')
contract=json.loads((ROOT/'analytics/data-contract.json').read_text())
(definition/'model.tmdl').write_text('model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tsourceQueryCulture: en-US\n\n'+''.join(f'ref table {name}\n' for name in contract)+'ref role StudentAccess\n',encoding='utf-8')
text=(ROOT/'analytics/measures.dax').read_text()
measures=re.findall(r'MEASURE (\w+)\[([^\]]+)\] =\s*(.*?)(?=\n    MEASURE |\nEVALUATE)',text,re.S)
catalog=[]
for name,spec in contract.items():
    query=(ROOT/spec['query_file']).read_text()
    types=dict(re.findall(r'\{"(\w+)", (type \w+|Int64.Type)\}',query))
    content=f'table {name}\n\tlineageTag: {uuid.uuid5(uuid.NAMESPACE_URL,name)}\n'
    for col in spec['columns']:
        dtype={'type number':'double','Int64.Type':'int64','type logical':'boolean','type text':'string'}[types[col]]
        content+=f'\n\tcolumn {col}\n\t\tdataType: {dtype}\n\t\tsourceColumn: {col}\n\t\tsummarizeBy: none\n'
        if name.startswith('Dim_') and name!='Dim_UserAccess' and col=={'Dim_Student':'student_id','Dim_Class':'class_id','Dim_Subject':'subject_id','Dim_Term':'term_id'}.get(name):content+='\t\tisKey\n'
    for table,title,expression in measures:
        if table!=name:continue
        expression=expression.strip()
        content+="\n\tmeasure '"+title+"' =\n"+'\n'.join('\t\t\t'+line.strip() for line in expression.splitlines())+'\n\t\tformatString: '+('0.0%' if title=='Support Attendance Rate' else '0.00' if any(w in title for w in ['Score','Attendance','Trend']) and not title.startswith('Support') else '#,0')+'\n'
        catalog.append({'measureName':title,'tableName':table,'expression':expression,'owner':'TEAM-BLACKCATS','status':'Draft pending Desktop validation'})
    content+=f'\n\tpartition {name} = m\n\t\tmode: import\n\t\tsource =\n'+'\n'.join('\t\t\t\t'+line for line in query.splitlines())+'\n'
    (definition/'tables'/f'{name}.tmdl').write_text(content,encoding='utf-8')
relationships=[('Dim_Class','Dim_Student','class_id')]+[('Dim_Student',f,'student_id') for f in ['Fact_Performance','Fact_Status','Fact_Intervention','Fact_Submission','Fact_Report']]+[('Dim_Subject',f,'subject_id') for f in ['Fact_Performance','Fact_Intervention']]+[('Dim_Term',f,'term_id') for f in ['Fact_Performance','Fact_Status','Fact_Report']]
(definition/'relationships.tmdl').write_text('\n'.join(f'relationship {uuid.uuid5(uuid.NAMESPACE_URL,one+many+key)}\n\tfromColumn: {many}.{key}\n\ttoColumn: {one}.{key}\n\tcrossFilteringBehavior: oneDirection\n' for one,many,key in relationships),encoding='utf-8')
role='role StudentAccess\n\tmodelPermission: read\n'
rls=(ROOT/'analytics/rls.dax').read_text()
for table in ['Dim_UserAccess','Dim_Student','Dim_Class']:
    expression=rls.split('-- '+table+':\n')[1].split('\n\n--')[0].strip()
    role+=f'\n\ttablePermission {table} =\n'+'\n'.join('\t\t\t'+line for line in expression.splitlines())+'\n'
(definition/'roles/StudentAccess.tmdl').write_text(role,encoding='utf-8')
(ROOT/'analytics/AtRiskModel/codex-model-drafts/measure-drafts.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
(ROOT/'analytics/model-draft/README.md').write_text('''# Native semantic-model source — draft

Contains ten typed CSV import tables, 11 single-direction relationships, 21 DAX measures, and a dynamic StudentAccess role. This is reviewable TMDL source, not a Desktop-validated or published report. No PBIX/PBIT binary is edited.

Create and save a PBIP in Power BI Desktop, retain its native report and settings, and apply the reviewed semantic-model source to that project. Configure CSV paths and refresh; reconcile with the API and test RLS with every identity. See ../POWER-BI.md. Desktop validation cannot be performed on the current machine because Power BI Desktop was not found.
''',encoding='utf-8')
