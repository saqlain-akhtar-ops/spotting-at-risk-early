"""Validate flat star-schema CSVs before BI import, including corrupt input fixtures."""
import csv, json, argparse
from pathlib import Path
from collections import Counter
def read(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def validate(folder):
    folder=Path(folder);rows=read(folder/'Fact_Performance.csv')
    refs={k:{r[k] for r in read(folder/f'{name}.csv')} for k,name in [('student_id','Dim_Student'),('class_id','Dim_Class'),('subject_id','Dim_Subject'),('term_id','Dim_Term')]}
    counts=Counter();seen_ids=set();seen_grain=set();issues=[]
    for index,r in enumerate(rows,2):
        grain=tuple(r[k] for k in ['student_id','subject_id','term_id'])
        if r['performance_id'] in seen_ids or grain in seen_grain:counts['duplicate']+=1;issues.append({'row':index,'type':'duplicate'})
        seen_ids.add(r['performance_id']);seen_grain.add(grain)
        if not r.get('score'):counts['missing_mark']+=1;issues.append({'row':index,'type':'missing_mark'})
        for field in ['score','attendance']:
            if not r.get(field):continue
            try:
                number=float(r[field]);valid=0<=number<=100
            except (ValueError,TypeError):valid=False
            if not valid:counts['invalid_'+field]+=1;issues.append({'row':index,'type':'invalid_'+field})
        for key,values in refs.items():
            if r.get(key) not in values:counts['orphan']+=1;issues.append({'row':index,'type':'orphan','key':key})
    expected=len(refs['student_id'])*len(refs['subject_id'])*len(refs['term_id'])
    return {'passed':not issues,'records':len(rows),'counts':dict(counts),'absent_assessments':max(0,expected-len(seen_grain)),'issues':issues}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',nargs='?',default='analytics/export');args=parser.parse_args()
    result=validate(args.folder);print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
