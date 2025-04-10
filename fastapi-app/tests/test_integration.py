# tests/test_integration.py
import requests

def test_root():
    # 실제 배포된 서버 주소 (EC2 퍼블릭 IP와 포트)
    url = "http://3.37.127.42:8000/"
    response = requests.get(url)

    assert response.status_code == 200
    assert "Welcome! this is pytest + requests!" in response.text  # 응답 내용에 따라 수정해도 돼
