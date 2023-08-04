import sqlite3

def setup_database():
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            subject TEXT,
            sender TEXT,
            received TEXT,
            status TEXT,
            action_taken INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    return conn

def insert_email_if_not_exists(conn, email):
    c = conn.cursor()
    c.execute('''
        INSERT INTO emails (id, subject, sender, received, status) 
        SELECT ?, ?, ?, ?, ?
        WHERE NOT EXISTS(SELECT 1 FROM emails WHERE id = ?)
    ''', (email['id'], email['subject'], email['from']['emailAddress']['address'], email['receivedDateTime'], 'unread', email['id']))
    conn.commit()

def check_new_email():
    conn = sqlite3.connect('email_db.sqlite')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM emails WHERE responded=0 AND is_unread=1")
    new_email = cursor.fetchone()

    conn.close()

    return new_email