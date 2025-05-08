FROM python:3.9

# 앱 디렉토리 생성
WORKDIR /app

# 비루트 사용자 추가
RUN useradd -m appuser

# 파일 복사 및 설치
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# 실행 사용자 전환
USER appuser

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
