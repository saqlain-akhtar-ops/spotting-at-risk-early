from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.dialects import mysql
from backend.models import Base, ROOT
ddl=['-- MySQL 8 operational schema. Create a dedicated database and limited user first.']
for table in Base.metadata.sorted_tables:
    ddl.append(str(CreateTable(table).compile(dialect=mysql.dialect()))+';')
    ddl.extend(str(CreateIndex(i).compile(dialect=mysql.dialect()))+';' for i in table.indexes)
(ROOT/'docs/mysql-schema.sql').write_text('\n\n'.join(ddl),encoding='utf-8')
