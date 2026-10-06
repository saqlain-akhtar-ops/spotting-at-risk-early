from pathlib import Path
import csv, shutil
from tools.dq_checks import validate

def test_csv_corruption_is_detected_without_changing_sources(tmp_path):
    source=tmp_path/'clean';source.mkdir()
    tables={'Dim_Student':(['student_id'],[{'student_id':str(i)} for i in range(1,101)]),'Dim_Class':(['class_id'],[{'class_id':'1'}]),'Dim_Subject':(['subject_id'],[{'subject_id':'1'}]),'Dim_Term':(['term_id'],[{'term_id':'1'}]),
            'Fact_Performance':(['performance_id','student_id','class_id','subject_id','term_id','score','attendance'],[{'performance_id':str(i),'student_id':str(i),'class_id':'1','subject_id':'1','term_id':'1','score':'80','attendance':'90'} for i in range(1,101)])}
    for name,(columns,entries) in tables.items():
        with (source/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(entries)
    for p in source.glob('*.csv'):shutil.copy2(p,tmp_path/p.name)
    path=tmp_path/'Fact_Performance.csv'
    with path.open(encoding='utf-8-sig') as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    for i in range(3):rows[i]['score']='101'
    for i in range(3,79):rows[i]['score']=''
    rows.append(dict(rows[-1]))
    rows[80]['student_id']='999999'
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    result=validate(tmp_path)
    assert not result['passed']
    assert result['counts']=={'invalid_score':3,'missing_mark':76,'orphan':1,'duplicate':1}
    assert validate(source)['passed']
