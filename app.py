import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, jsonify, abort

app = Flask(__name__, static_folder='static', template_folder='templates')

# 최종 제품 및 카테고리 데이터
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

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def home():
    # 실시간 현황은 임시 데이터(DB 대신)로 보여줍니다.
    temp_consultations = [
        {'name': '홍길동', 'address': '서울시 종로구', 'created_at': '2025-07-21', 'product': '해충 방제 솔루션'},
        {'name': '김영희', 'address': '경기도 성남시 분당구', 'created_at': '2025-07-21', 'product': '아이콘 정수기 II'},
    ]

    processed_consultations = []
    for item in temp_consultations:
        processed_item = dict(item)
        
        name = item.get('name', '')
        address = item.get('address', '')
        
        if name:
            processed_item['masked_name'] = name[0] + '**'
        else:
            processed_item['masked_name'] = '***'

        processed_item['masked_address'] = address[:3]
        processed_item['formatted_date'] = item['created_at'][:10]
        processed_consultations.append(processed_item)

    return render_template('index.html', consultations=processed_consultations, products=products_data, categories=categories_info)

# [추가됨] 누락되었던 제품 상세 페이지 경로
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products_data if p['id'] == product_id), None)
    if product is None:
        abort(404)
    return render_template('product-detail.html', product=product)

@app.route('/contact')
def contact():
    contact_categories = {k: v for k, v in categories_info.items() if k != 'all'}
    return render_template('contact.html', categories=contact_categories)

# [수정됨] DB 저장 대신 메일 발송
@app.route('/submit-consultation', methods=['POST'])
def submit_consultation():
    data = request.get_json()
    try:
        sender_email = os.environ.get('cescohyun@gmail.com')
        sender_password = os.environ.get('@HSld240486')
        receiver_email = os.environ.get('cescohyun@gmail.com')

        subject = f"[케어 솔루션] 새로운 상담 신청: {data.get('name')}님"
        body = f"""
        새로운 상담 신청이 접수되었습니다.
        - 이름: {data.get('name')}
        - 연락처: {data.get('phone')}
        - 주소: {data.get('address')}
        - 관심 제품: {data.get('product')}
        """
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print(f"메일 발송 성공: {data.get('name')}님")
    except Exception as e:
        print(f"Mail Error: {e}")
        return jsonify({'result': 'error', 'message': '신청 접수 중 오류가 발생했습니다.'}), 500
    
    return jsonify({'result': 'success', 'message': '상담 신청이 성공적으로 접수되었습니다.'})

if __name__ == '__main__':
    app.run(debug=True)