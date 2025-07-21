import os
import psycopg2

# app.py의 get_db_connection()과 동일한 함수
def get_db_connection():
    conn_str = os.environ.get('DATABASE_URL')
    if conn_str is None:
        raise ValueError("DATABASE_URL 환경 변수가 설정되지 않았습니다.")
    conn = psycopg2.connect(conn_str)
    return conn

# 테이블을 생성하는 함수
def initialize_database():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS consultations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            phone VARCHAR(100) NOT NULL,
            address VARCHAR(255) NOT NULL,
            product VARCHAR(100) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()
    print("Table 'consultations' initialized successfully.")

# 이 파일이 직접 실행될 때 함수를 호출
if __name__ == '__main__':
    initialize_database()