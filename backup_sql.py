import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def _yes_no(name: str, default: str = "no") -> str:
    value = os.getenv(name, default).strip().lower()
    if value not in {"yes", "no"}:
        raise ValueError(
            f"{name} must be 'yes' or 'no', got {value!r}"
        )
    return value

def get_connection(database):
    """ Establishes a connection to the SQL Server Database """
    server = os.getenv("SERVER")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DRIVER")  # Ensure you have the correct ODBC driver installed
    trust_cert = _yes_no("DB_TRUST_SERVER_CERT", default="no")

    try:
        conn = pyodbc.connect(
            f'DRIVER={driver};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
            f"TrustServerCertificate={trust_cert};"
        )
        return conn
    except Exception as e:
        print(f"Error while trying to connect to database: {e}")
        raise

def create_backup():
    """Creates a database backup and returns its path in the file system."""
    try:
        backup_dir = os.getenv("BACKUP_DIR")
        host_backup_dir = os.getenv("HOST_BACKUP_DIR")
        database = os.getenv("DB")

        if host_backup_dir == None:
            host_backup_dir = backup_dir

        conn = get_connection(database)    
        # Pyodbc needs to have the autocommit option set as true
        # to perform backup operations
        conn.autocommit = True
        
        cursor = conn.cursor()

        timestamp = str(datetime.now().strftime('%Y%m%d_%H%M%S'))
        backup_file = f'{database}_{timestamp}.bak'

        backup_path = os.path.join(backup_dir, backup_file)
        print(backup_path)

        backup_sql = f"""
        BACKUP DATABASE [{database}] TO DISK = N'{backup_path}' WITH NOFORMAT, NOINIT, NAME = '{database}-full', SKIP, NOREWIND, NOUNLOAD, STATS = 10
        """
        print(backup_sql)

        cursor.execute(backup_sql)

        while (cursor.nextset()):
            pass

        host_backup_dir = os.path.join(host_backup_dir, backup_file)

        return host_backup_dir
        
    except Exception as e:
        print(f"Error while creating the backup: {e}")
        return None
