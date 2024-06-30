from flask import Flask, Response, request, render_template
import numpy as np
import cv2

app = Flask(__name__)

# 이미지를 저장할 전역 변수
global_frame = None

# 이미지를 받는 엔드포인트
@app.route('/receive', methods=['POST'])
def receive():
    global global_frame
    try:
        # 전송된 이미지 받기
        img_text = request.data
        
        # 텍스트를 바이너리 데이터로 변환
        img_array = np.frombuffer(img_text, dtype=np.uint8)
        
        # 바이너리 데이터를 이미지로 디코딩
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # 전역 변수에 저장
        global_frame = frame
        
        # 전송 완료 메시지 반환
        return "이미지 수신 완료"
    
    except Exception as e:
        print(f"예외 발생: {e}")
        return "이미지 수신 중 오류 발생"

# 웹페이지 송출 엔드포인트 (GET 요청만 처리)
@app.route('/')
def index():
    return render_template('index.html')

# 이미지를 스트리밍하는 엔드포인트 (GET 요청만 처리)
def generate():
    global global_frame
    while True:
        if global_frame is not None:
            # 이미지를 JPEG 포맷으로 인코딩
            ret, jpeg = cv2.imencode('.jpg', global_frame)
            frame = jpeg.tobytes()
            
            # 이미지 스트리밍
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
