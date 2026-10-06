"""Start or check only the isolated project MySQL instance."""
from pathlib import Path
import sys,json,socket,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.runtime')]
import pymysql
DATA=ROOT/'data/mysql-project'
BASE=Path('C:/Program Files/MySQL/MySQL Server 8.0')
def start():
    if not (DATA/'administration.json').exists():raise RuntimeError('Project MySQL has not been configured')
    config=json.loads((DATA/'administration.json').read_text())
    with socket.socket() as sock:
        listening=sock.connect_ex((config['host'],config['port']))==0
    if not listening:
        subprocess.Popen([str(BASE/'bin/mysqld.exe'),'--no-defaults',f'--basedir={BASE}',f'--datadir={DATA}',
            f'--port={config["port"]}','--bind-address=127.0.0.1','--mysqlx=0',
            f'--pid-file={DATA/"server.pid"}',f'--log-error={DATA/"server.log"}'],
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=0x08000000)
    for attempt in range(30):
        try:
            connection=pymysql.connect(host=config['host'],port=config['port'],user=config['user'],password=config['password'])
        except pymysql.err.OperationalError:
            if listening or attempt==29:raise RuntimeError('Cannot authenticate the isolated project MySQL instance') from None
            time.sleep(1);continue
        with connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT @@datadir, VERSION()');directory,version=cursor.fetchone()
                if Path(directory).resolve()!=DATA.resolve():raise RuntimeError('Port belongs to another database instance; refusing to manage it')
        return version
if __name__=='__main__':
    try:print(f'Project MySQL {start()} ready on 127.0.0.1:3307')
    except RuntimeError as error:raise SystemExit(str(error))
