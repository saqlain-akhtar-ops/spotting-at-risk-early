"""Create an isolated, loopback-only MySQL project server without altering MySQL80."""
from pathlib import Path
import os,subprocess,sys,secrets,re,socket,time,json
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.runtime')]
import pymysql
from pymysql.constants import CLIENT
BASE=Path('C:/Program Files/MySQL/MySQL Server 8.0')
DATA=ROOT/'data/mysql-project'
PORT=3307

def main():
    config=ROOT/'.env.local'
    if config.exists():raise SystemExit('.env.local already exists; preserving its configured connection')
    recovering=DATA.exists() and (DATA/'initialize.log').exists() and (DATA/'server.pid').exists()
    if DATA.exists() and not recovering:raise SystemExit('Project MySQL directory already exists; refusing to reinitialize it')
    if not recovering:
        with socket.socket() as sock:sock.bind(('127.0.0.1',PORT))
        DATA.mkdir(parents=True)
    init_log=DATA/'initialize.log'
    command=[str(BASE/'bin/mysqld.exe'),'--no-defaults','--initialize',f'--basedir={BASE}',f'--datadir={DATA}',f'--log-error={init_log}']
    result=None if recovering else subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000)
    if result is not None and result.returncode:raise SystemExit('MySQL initialization failed; inspect the local initialization log without sharing passwords')
    temporary=re.search(r'temporary password is generated for root@localhost: (.+)',init_log.read_text(encoding='utf-8',errors='replace'))
    if not temporary:raise SystemExit('Temporary credential could not be read from the local initialization log')
    args=[str(BASE/'bin/mysqld.exe'),'--no-defaults',f'--basedir={BASE}',f'--datadir={DATA}',f'--port={PORT}','--bind-address=127.0.0.1','--mysqlx=0',f'--pid-file={DATA/"server.pid"}',f'--log-error={DATA/"server.log"}']
    process=None if recovering else subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)
    root_password=secrets.token_urlsafe(32);app_password=secrets.token_urlsafe(32)
    # The official client supports expired-password bootstrap without issuing
    # session setup queries first. Credentials stay out of command arguments.
    client_env=os.environ.copy();client_env['MYSQL_PWD']=temporary.group(1).strip()
    result=subprocess.run([str(BASE/'bin/mysql.exe'),'--no-defaults','--connect-expired-password',
        '--protocol=TCP','--host=127.0.0.1',f'--port={PORT}','--user=root'],
        input=f"ALTER USER 'root'@'localhost' IDENTIFIED BY '{root_password}';\n".encode(),
        env=client_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000)
    if result.returncode:
        code=re.search(rb'ERROR (\d+)',result.stderr)
        raise SystemExit('MySQL credential bootstrap failed'+(' (error '+code.group(1).decode()+')' if code else ''))
    (DATA/'administration.json').write_text(json.dumps({'host':'127.0.0.1','port':PORT,'user':'root','password':root_password,'server_pid':int((DATA/'server.pid').read_text().strip())},indent=2),encoding='utf-8')
    connection=pymysql.connect(host='127.0.0.1',port=PORT,user='root',password=root_password,autocommit=True)
    with connection.cursor() as cursor:
        cursor.execute('CREATE DATABASE spotting_at_risk CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        cursor.execute("CREATE USER 'at_risk_app'@'localhost' IDENTIFIED BY %s",(app_password,))
        cursor.execute("GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX,REFERENCES,DROP ON spotting_at_risk.* TO 'at_risk_app'@'localhost'")
    connection.close()
    (DATA/'administration.json').write_text(json.dumps({'host':'127.0.0.1','port':PORT,'user':'root','password':root_password,'server_pid':int((DATA/'server.pid').read_text().strip())},indent=2),encoding='utf-8')
    config.write_text(f'APP_ENV=development\nDEMO_SEED=1\nDATABASE_URL=mysql+pymysql://at_risk_app:{app_password}@127.0.0.1:{PORT}/spotting_at_risk?charset=utf8mb4\nCOOKIE_SECURE=false\nALLOWED_HOSTS=localhost,127.0.0.1\n',encoding='utf-8')
    init_log.unlink()
    print(f'Project MySQL is running on 127.0.0.1:{PORT}; dedicated database created and local configuration saved. No passwords printed.')
if __name__=='__main__':main()
