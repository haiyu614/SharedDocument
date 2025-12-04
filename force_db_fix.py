import os
import pymysql
from config import Config

# Parse database URL
db_url = Config.SQLALCHEMY_DATABASE_URI
# Assuming format mysql+pymysql://user:password@host/dbname
# This is a bit fragile parsing but works for standard connection strings
try:
    # Remove prefix
    url_parts = db_url.replace('mysql+pymysql://', '').split('/')
    if len(url_parts) < 2:
        raise ValueError("Invalid DB URL format")
    
    db_name = url_parts[1].split('?')[0]
    credentials = url_parts[0].split('@')
    host_port = credentials[1].split(':')
    host = host_port[0]
    port = 3306
    if len(host_port) > 1:
        port = int(host_port[1])
        
    user_pass = credentials[0].split(':')
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ''

    print(f"Connecting to {host}:{port} as {user}...")
    
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
        port=port,
        cursorclass=pymysql.cursors.DictCursor
    )

    with connection.cursor() as cursor:
        print("Checking for document_shares table...")
        cursor.execute("SHOW TABLES LIKE 'document_shares'")
        result = cursor.fetchone()
        
        if not result:
            print("Creating document_shares table manually...")
            sql = """
            CREATE TABLE IF NOT EXISTS document_shares (
                id INT AUTO_INCREMENT PRIMARY KEY,
                document_id INT NOT NULL,
                user_id INT NOT NULL,
                permission VARCHAR(20) DEFAULT 'view',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_share (document_id, user_id),
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            cursor.execute(sql)
            connection.commit()
            print("Table document_shares created successfully.")
        else:
            print("Table document_shares already exists.")

    connection.close()

except Exception as e:
    print(f"Error: {e}")
