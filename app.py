import os
import psycopg2 # sqlite3 대신 psycopg2를 사용합니다.
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__, static_folder='static', template_folder='templates')

# 사용자님이 업데이트한 제품 및 카테고리 데이터
products_data = [
    {'id': 1, 'name': '해충 방제 솔루션', 'original_price': 0, 'price': 0, 'description': '가정/사업장 맞춤 방제 플랜 상담', 'image_url': '/static/images/product-ipm.jpg', 'category': 'ipm'},
    {'id': 2, 'name': '바이러스케어 솔루션', 'original_price': 0, 'price': 0, 'description': '공간 살균 및 유해세균 제어 상담', 'image_url': '/static/images/product-ipm-2.jpg', 'category': 'ipm'},
    {'id': 3, 'name': '에어퍼퓸', 'original_price': 56900, 'price': 48900, 'description': '공간을 채우는 프리미엄 향기', 'image_url': '/static/images/product-perfume.jpg', 'category': 'air_perfume'},
    {'id': 4, 'name': '에어제닉', 'original_price': 24900, 'price': 22900, 'description': '공간을 채우는 프리미엄 향기', 'image_url': '/static/images/product_aerogenic.jpg', 'category': 'air_perfume'},
    {'id': 6, 'name': '새니제닉', 'original_price': 24900, 'price': 22900, 'description': '물 없이도 유해세균 99.9% 살균', 'image_url': '/static/images/product_sanigenic.jpg', 'category': 'air_perfume'},
    {'id': 5, 'name': '핸드제닉', 'original_price': 24900, 'price': 22900, 'description': '비접촉식 거품형으로 교차오염없이', 'image_url': '/static/images/product_handgenic.jpg', 'category': 'air_perfume'},
    {'id': 7, 'name': '핸드 드라이어', 'original_price': 24900, 'price': 22900, 'description': '종이 타월대비 비용 절감 효과', 'image_url': '/static/images/product_handdryer.jpg', 'category': 'air_perfume'},
    {'id': 8, 'name': '판테온 공기살균/청정기', 'original_price': 52900, 'price': 45900, 'description': '바이러스와 세균을 한번에 제거', 'image_url': '/static/images/product-sterilizer.jpg', 'category': 'air_purifier'},
    {'id': 9, 'name': '듀얼케어 공기청정기', 'original_price': 55900, 'price': 48900, 'description': '360도 강력한 청정 효과', 'image_url': '/static/images/product-air-purifier.jpg', 'category': 'air_purifier'},
    {'id': 10, 'name': '가정용 살균온정수기', 'original_price': 32900, 'price': 29900, 'description': '컴팩트한 디자인, 스마트한 기능', 'image_url': '/static/images/product-water-purifier-1.jpg', 'category': 'water_purifier'},
    {'id': 11, 'name': '업소용 스탠드 정수기', 'original_price': 38900, 'price': 25900, 'description': '넉넉한 용량의 비즈니스 솔루션', 'image_url': '/static/images/product-water-purifier-2.jpg', 'category': 'water_purifier'},
    {'id': 12, 'name': '스마트 비데', 'original_price': 19900, 'price': 15900, 'description': '위생적인 스테인리스 노즐', 'image_url': '/static/images/product-bidet.jpg', 'category': 'bidet'},
    {'id': 13, 'name': '에어커튼 실외용 1000', 'original_price': 22900, 'price': 19900, 'description': '외부 공기, 먼지, 해충의 실내 유입을 강력하게 차단합니다.', 'image_url': '/static/images/product_air_curtain_out_1000.jpg', 'category': 'air_curtain'},
]

categories_info = {
    'all': '전체보기', 'ipm': 'IPM(해충방제)', 'air_perfume': '방향/세정/건조기',
    'air_purifier': '공기살균기/청정기', 'water_purifier': '정수기',
    'bidet': '비데', 'air_curtain': '에어커튼'
}

# [수정됨] 데이터베이스 연결을 위한 함수
def get_db_connection():
    conn_str = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(conn_str)
    return conn

# [수정됨] PostgreSQL에 맞게 테이블 초기화 함수 수정
def init_db():
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

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM consultations ORDER BY created_at DESC LIMIT 7")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    raw_consultations = [dict(zip(columns, row)) for row in rows]
    cur.close()
    conn.close()

    processed_consultations = []
    for item in raw_consultations:
        processed_item = dict(item)
        processed_item['masked_address'] = item['address'].split(' ')[0]
        processed_item['formatted_date'] = item['created_at'].strftime('%Y-%m-%d')
        processed_consultations.append(processed_item)

    return render_template('index.html', consultations=processed_consultations, products=products_data, categories=categories_info)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products_data if p['id'] == product_id), None)
    if product is None:
        abort(404)
    return render_template('product-detail.html', product=product)

@app.route('/contact')
def contact():
    # 'Mylab'이 'air_curtain'으로 바뀌었으므로, 이제 상담신청에서 제외할 카테고리가 없습니다.
    # 만약 에어커튼도 제외하려면 if k not in ['all', 'air_curtain'] 을 유지하세요.
    contact_categories = {k: v for k, v in categories_info.items() if k != 'all'}
    return render_template('contact.html', categories=contact_categories)

@app.route('/submit-consultation', methods=['POST'])
def submit_consultation():
    data = request.get_json()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO consultations (name, phone, address, product) VALUES (%s, %s, %s, %s)",
                    (data['name'], data['phone'], data['address'], data['product']))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")
        return jsonify({'result': 'error', 'message': '데이터 저장 중 오류가 발생했습니다.'}), 500
    
    return jsonify({'result': 'success', 'message': '상담 신청이 성공적으로 접수되었습니다.'})

# Render 서버에서는 이 부분이 직접 실행되지 않으므로, init_db()를 맨 아래에서 위로 옮겼습니다.
# 로컬 테스트 시에는 init_db()가 필요할 수 있습니다.
# init_db() 

if __name__ == '__main__':
    # 로컬에서 실행할 때만 DB를 초기화하려면 이 안에 init_db()를 넣는 것이 좋습니다.
    init_db()
    app.run(debug=True)