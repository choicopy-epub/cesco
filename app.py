import sqlite3
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__, static_folder='static', template_folder='templates')

# 제품 및 카테고리 데이터 정의
products_data = [
    {'id': 1, 'name': '해충 방제 솔루션', 'price': 0, 'description': '가정/사업장 맞춤 방제 플랜 상담', 'image_url': '/static/images/product-ipm.jpg', 'category': 'ipm'},
    {'id': 2, 'name': '바이러스케어 솔루션', 'price': 0, 'description': '공간 살균 및 유해세균 제어 상담', 'image_url': '/static/images/product-ipm-2.jpg', 'category': 'ipm'},
    {'id': 3, 'name': '에어퍼퓸', 'price': 48900, 'description': '공간을 채우는 프리미엄 향기', 'image_url': '/static/images/product-perfume.jpg', 'category': 'air_perfume'},
    {'id': 4, 'name': '케어 공기살균기', 'price': 39900, 'description': '바이러스와 세균을 한번에 제거', 'image_url': '/static/images/product-sterilizer.jpg', 'category': 'air_purifier'},
    {'id': 5, 'name': '케어 공기청정기', 'price': 43900, 'description': '360도 강력한 청정 효과', 'image_url': '/static/images/product-air-purifier.jpg', 'category': 'air_purifier'},
    {'id': 6, 'name': '살균온 정수기', 'price': 25900, 'description': '컴팩트한 디자인, 스마트한 기능', 'image_url': '/static/images/product-water-purifier-1.jpg', 'category': 'water_purifier'},
    {'id': 7, 'name': '업소용 스탠드 정수기', 'price': 33900, 'description': '넉넉한 용량의 비즈니스 솔루션', 'image_url': '/static/images/product-water-purifier-2.jpg', 'category': 'water_purifier'},
    {'id': 8, 'name': '스마트 비데', 'price': 15900, 'description': '위생적인 스테인리스 노즐', 'image_url': '/static/images/product-bidet.jpg', 'category': 'bidet'},
    {'id': 9, 'name': '마이랩 친환경 주방세제', 'price': 9900, 'description': '자연 유래 성분으로 안심 설거지', 'image_url': '/static/images/product-mylab.jpg', 'category': 'mylab'},
]

categories_info = {
    'all': '전체보기', 'ipm': 'IPM(해충방제)', 'air_perfume': '에어퍼퓸',
    'air_purifier': '공기살균기/청정기', 'water_purifier': '정수기',
    'bidet': '비데', 'mylab': 'Mylab'
}

def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('CREATE TABLE IF NOT EXISTS consultations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT NOT NULL, address TEXT NOT NULL, product TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);')
    conn.close()

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row 
    cur = conn.cursor()
    cur.execute("SELECT * FROM consultations ORDER BY created_at DESC LIMIT 5")
    raw_consultations = cur.fetchall()
    conn.close()

    processed_consultations = []
    for item in raw_consultations:
        processed_item = dict(item)
        processed_item['masked_address'] = item['address'].split(' ')[0]
        processed_item['formatted_date'] = item['created_at'][:10]
        processed_consultations.append(processed_item)

    return render_template('index.html', consultations=processed_consultations, products=products_data, categories=categories_info)

# app.py

# ... home() 함수 아래에 추가 ...

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # products_data 리스트에서 id가 일치하는 제품을 찾습니다.
    product = next((p for p in products_data if p['id'] == product_id), None)
    
    # 만약 제품을 찾지 못하면 404 Not Found 에러를 표시합니다.
    if product is None:
        abort(404)
        
    # product-detail.html을 보여줄 때, 찾은 제품 정보를 함께 전달합니다.
    return render_template('product-detail.html', product=product)

@app.route('/contact')
def contact():
    contact_categories = {k: v for k, v in categories_info.items() if k not in ['all', 'mylab']}
    return render_template('contact.html', categories=contact_categories)

@app.route('/submit-consultation', methods=['POST'])
def submit_consultation():
    data = request.get_json()
    try:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO consultations (name, phone, address, product) VALUES (?,?,?,?)",
                    (data['name'], data['phone'], data['address'], data['product']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'result': 'error', 'message': '데이터 저장 중 오류가 발생했습니다.'}), 500
    finally:
        conn.close()
    return jsonify({'result': 'success', 'message': '상담 신청이 성공적으로 접수되었습니다.'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)