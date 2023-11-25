import subprocess
import datetime
import time


def create_backup():
    mongo_host = '0.0.0.0'  # Change this to your MongoDB host
    mongo_port = '27017'  # Change this to your MongoDB port
    db_name = 'boostupauth'  # Change this to your database name
    backup_dir = 'backups'  # Change this to your desired backup directory

    # Generate timestamp for backup file
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file = f'{db_name}_backup_{timestamp}'

    # Run mongodump command
    command = f'mongodump --host {mongo_host} --port {mongo_port} --db {db_name} --out {backup_dir}/{backup_file}'

    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Backup created successfully: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Backup failed: {e}")


while True:
    create_backup()
    time.sleep(1000)

