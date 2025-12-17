from db2 import get_db
from datetime import datetime

def create_record():
    check_tables_exist()

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO records (start_time, status)
        VALUES (%s, 'Running')
    """, (datetime.now(),))

    db.commit()
    record_id = cursor.lastrowid 

    cursor.close()
    db.close()
    return record_id

def finish_record(record_id, items):
    check_tables_exist()
    
    db = get_db()
    cursor = db.cursor()

    for item in items:
        cursor.execute("""
            INSERT INTO record_item (
                item_id,
                record_id,
                scanner_1,
                scanner_2,
                scanner_3,
                result,
                fallback
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            item["item_id"],
            record_id,
            item.get("scanner_1"),
            item.get("scanner_2"),
            item.get("scanner_3"),
            item["result"],
            item["fallback"]
        ))

    cursor.execute("""
        UPDATE records
        SET end_time=%s,
            total_items=%s,
            status='Completed',
        WHERE id=%s;
    """, (datetime.now(), len(items), record_id))

    db.commit()
    cursor.close()
    db.close()

def check_tables_exist():
    db = get_db()
    cursor = db.cursor()

    # records table
    cursor.execute("""
        CREATE TABLE IF NOT EXIST records (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            batch_code VARCHAR(50) UNIQUE,
            start_time DATETIME,
            end_time DATETIME,
            total_items INT DEFAULT 0,
            status ENUM('Running', 'Completed', 'Failed'),
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # record_item table
    cursor.execute("""
        CREATE TABLE IF NOT EXIST record_item (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            item_id BIGINT,
            record_id BIGINT,
            scanner_1 VARCHAR(20),
            scanner_2 VARCHAR(20),
            scanner_3 VARCHAR(20),
            result ENUM('Pass', 'Fail', 'Unknown'),\
            fallback BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   
            FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE
        )
    """)

    db.commit()
    cursor.close()
    db.close()