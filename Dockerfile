# AI Trends Dashboard - 프로덕션 Dockerfile

FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 프로젝트 파일 복사
COPY requirements.txt .
COPY agent_harness/ ./agent_harness/
COPY tests/ ./tests/
COPY *.py ./
COPY *.md ./
COPY *.html ./

# Python 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 환경변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONENCODING=utf-8
ENV AGENT_EFFORT=high
ENV MAX_ITERATIONS=10

# 로그 디렉토리 생성
RUN mkdir -p logs

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/economics_news_advanced.html || exit 1

# 포트 노출
EXPOSE 8000

# 기본 명령어: 웹 서버 + 스케줄러 시작
CMD ["sh", "-c", "python -m http.server 8000 & python daily_economics_scheduler.py"]
