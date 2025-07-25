import os
import smtplib
import psycopg2
from email.mime.text import MIMEText
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__, static_folder='static', template_folder='templates')

# --- 제품 및 카테고리 데이터 ---
# (이전과 동일한 products_data, categories_info)
products_data = [
    {'id': 1, 'name': '해충 방제 솔루션', 'original_price': 0, 'price': 0, 'description': '가정/사업장 맞춤 방제 플랜 상담', 'image_url': '/static/images/product-ipm.jpg', 'category': 'ipm'},
    {'id': 2, 'name': '긴급진단 솔루션', 'original_price': 0, 'price': 0, 'description': '공간 살균 및 유해세균 제어 상담', 'image_url': '/static/images/product-ipm-2.jpg', 'category': 'ipm'},
    {'id': 3, 'name': '에어퍼퓸', 'original_price': 87000, 'price': 48000, 'description': '공간을 채우는 프리미엄 향기', 'image_url': '/static/images/product-perfume.jpg', 'category': 'air_perfume'},
    {'id': 4, 'name': '에어제닉', 'original_price': 27900, 'price': 24900, 'description': '공간을 채우는 프리미엄 향기', 'image_url': '/static/images/product_aerogenic.jpg', 'category': 'air_perfume'},
    {'id': 5, 'name': '새니제닉', 'original_price': 30900, 'price': 27900, 'description': '물 없이도 유해세균 99.9% 살균', 'image_url': '/static/images/product_sanigenic.jpg', 'category': 'air_perfume'},
    {'id': 6, 'name': '핸드제닉', 'original_price': 30900, 'price': 27900, 'description': '비접촉식 거품형으로 교차오염없이', 'image_url': '/static/images/product_handgenic.jpg', 'category': 'air_perfume'},
    {'id': 7, 'name': '프레시제닉', 'original_price': 23900, 'price': 20900, 'description': '변기오염, 세정 살균 탈취 3중 관리', 'image_url': '/static/images/product_freshgenic.jpg', 'category': 'air_perfume'},
    {'id': 8, 'name': '핸드 드라이어', 'original_price': 25900, 'price': 20900, 'description': '종이 타월대비 비용 절감 효과', 'image_url': '/static/images/product_handdryer.jpg', 'category': 'air_perfume'},
    {'id': 9, 'name': '판테온 공기살균/청정기', 'original_price': 50900, 'price': 39900, 'description': '바이러스와 세균을 한번에 제거', 'image_url': '/static/images/product-sterilizer.jpg', 'category': 'air_purifier'},
    {'id': 10, 'name': 'UV파워 센스미 공기살균기', 'original_price': 37900, 'price': 22900, 'description': '구리필터 세균, 바이러스, 곰팡이 억제', 'image_url': '/static/images/product_senseme.jpg', 'category': 'air_purifier'},
    {'id': 11, 'name': '3up 공기청정기', 'original_price': 34900, 'price': 21900, 'description': '360도 강력한 청정 효과', 'image_url': '/static/images/product-air-purifier.jpg', 'category': 'air_purifier'},
    {'id': 12, 'name': '가정용 살균온정수기', 'original_price': 49900, 'price': 27900, 'description': '컴팩트한 디자인, 스마트한 기능', 'image_url': '/static/images/product-water-purifier-1.jpg', 'category': 'water_purifier'},
    {'id': 13, 'name': '업소용 스탠드 정수기', 'original_price': 29900, 'price': 14900, 'description': '넉넉한 용량의 비즈니스 솔루션', 'image_url': '/static/images/product-water-purifier-2.jpg', 'category': 'water_purifier'},
    {'id': 14, 'name': '살균방수 올인원 비데', 'original_price': 26900, 'price': 15900, 'description': '위생적인 스테인리스 노즐', 'image_url': '/static/images/product-bidet.jpg', 'category': 'bidet'},
    {'id': 15, 'name': '에어커튼 실외용 1000', 'original_price': 25900, 'price': 22900, 'description': '외부 공기, 먼지, 해충의 실내 유입을 강력하게 차단합니다.', 'image_url': '/static/images/product_air_curtain_out_1000.jpg', 'category': 'air_curtain'},
    {'id': 16, 'name': '에어커튼 실외용 900', 'original_price': 24900, 'price': 21900, 'description': '외부 공기, 먼지, 해충의 실내 유입을 강력하게 차단합니다.', 'image_url': '/static/images/product_air_curtain_out_1000.jpg', 'category': 'air_curtain'},
]
categories_info = { 'all': '전체보기', 'ipm': 'IPM(해충방제)', 'air_perfume': '방향/세정/건조기', 'air_purifier': '공기살균기/청정기', 'water_purifier': '정수기', 'bidet': '비데', 'air_curtain': '에어커튼' }

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# --- 데이터베이스 연결 함수 ---
def get_db_connection():
    conn_str = os.environ.get('DATABASE_URL')
    if conn_str is None:
        raise ValueError("DATABASE_URL 환경 변수가 설정되지 않았습니다.")
    conn = psycopg2.connect(conn_str)
    return conn

# --- 페이지 경로(라우트) 설정 ---
@app.route('/')
def home():
    processed_consultations = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM consultations ORDER BY created_at DESC LIMIT 7")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        raw_consultations = [dict(zip(columns, row)) for row in rows]
        cur.close()
        conn.close()
        for item in raw_consultations:
            processed_item = dict(item)
            processed_item['masked_address'] = item['address'].split(' ')[0]
            processed_item['formatted_date'] = item['created_at'].strftime('%Y-%m-%d')
            processed_item['masked_name'] = item['name'][0] + '**' if item['name'] else '***'
            processed_consultations.append(processed_item)
    except Exception as e:
        print(f"Home DB Error: {e}")

    return render_template('index.html', consultations=processed_consultations, products=products_data, categories=categories_info)

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
    # 'Mylab'이 'air_curtain'으로 바뀌었으므로, 이제 상담신청에서 제외할 카테고리가 없습니다.
    # 만약 에어커튼도 제외하려면 if k not in ['all', 'air_curtain'] 을 유지하세요.
    contact_categories = {k: v for k, v in categories_info.items() if k != 'all'}
    return render_template('contact.html', categories=contact_categories)

@app.route('/submit-consultation', methods=['POST'])
def submit_consultation():
    data = request.get_json()
    
    # 1. 메일 발송 시도
    try:
        sender_email = os.environ.get('cescohyun@gmail.com')
        sender_password = os.environ.get('@HSld240486')
        receiver_email = os.environ.get('cescohyun@gmail.com')
        
        subject = f"[케어 솔루션] 새로운 상담 신청: {data.get('name')}님"
        body = f"이름: {data.get('name')}\n연락처: {data.get('phone')}\n주소: {data.get('address')}\n관심 제품: {data.get('product')}"
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Mail sent for: {data.get('name')}")
    except Exception as e:
        print(f"Mail Error: {e}") # 메일 실패는 로그만 남기고 넘어감

    # 2. 데이터베이스에 저장 시도
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO consultations (name, phone, address, product) VALUES (%s, %s, %s, %s)",
                    (data['name'], data['phone'], data['address'], data['product']))
        conn.commit()
        cur.close()
        conn.close()
        print(f"DB save success for: {data.get('name')}")
    except Exception as e:
        print(f"Submit DB Error: {e}")
        # DB 저장에 실패하면 프론트엔드에 에러를 보낼 수 있지만, 메일은 갔을 수 있으므로 일단 성공으로 처리
        # 만약 DB 저장이 필수라면 여기서 에러를 반환해야 함
    
    return jsonify({'result': 'success', 'message': '상담 신청이 성공적으로 접수되었습니다.'})

# ... (나머지 /product/<id>, /contact 경로는 이전과 동일) ...

if __name__ == '__main__':
    app.run(debug=True)