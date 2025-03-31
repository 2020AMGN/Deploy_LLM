import requests
import json

# 서버 주소 설정 (실제 서버 IP로 변경 필요)
# SERVER_URL = "http://your_server_ip:8000"
SERVER_URL = "http://localhost:8000"

def test_number_endpoint():
    data = {"number": 5}
    response = requests.post(f"{SERVER_URL}/process_number", json=data)
    print("숫자 처리 결과:", response.json())

def test_english_endpoint():
    data = {"text": "Hello, this is a test message"}
    response = requests.post(f"{SERVER_URL}/process_english", json=data)
    print("영문 처리 결과:", response.json())

def test_korean_endpoint():
    data = {"text": "안녕하세요, 테스트 메시지입니다"}
    response = requests.post(f"{SERVER_URL}/process_korean", json=data)
    print("한글 처리 결과:", response.json())

if __name__ == "__main__":
    # 모든 엔드포인트 테스트
    test_number_endpoint()
    test_english_endpoint()
    test_korean_endpoint()