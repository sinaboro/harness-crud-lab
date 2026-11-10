# ============================================================
# Dockerfile - 이 과정에서 쓰는 "도구 상자" 이미지의 설계도
#
# 내 PC 에는 Docker Desktop 만 설치한다.
# Python, FastAPI, pytest, AI 에이전트(OpenCode)는 모두 이 이미지 안에 들어 있다.
# → 누구의 PC 에서나 똑같은 환경이 만들어진다.
# ============================================================

# 1) 파이썬 3.12 가 설치된 작은 리눅스에서 시작한다.
FROM python:3.12-slim

# 2) 파이썬 동작 방식 몇 가지를 정한다.
#    - PYTHONDONTWRITEBYTECODE: __pycache__ 폴더를 만들지 않는다(윈도우 폴더가 지저분해지지 않게)
#    - PYTHONUNBUFFERED: print 한 내용이 바로바로 화면에 보이게 한다
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 3) 리눅스 기본 도구 설치: git(저장), curl(내려받기), ripgrep(에이전트가 파일을 찾을 때 사용)
RUN apt-get update \
    && apt-get install -y --no-install-recommends bash ca-certificates curl git ripgrep tar \
    && rm -rf /var/lib/apt/lists/*

# 4) AI 에이전트 OpenCode 설치 (공식 설치 스크립트, 버전 고정)
#    버전을 고정하는 이유: 수업 도중에 도구가 저절로 바뀌어 화면이 달라지는 일을 막는다.
ARG OPENCODE_VERSION=2.2.6
RUN curl -fsSL https://opencode.ai/v2/install | bash -s -- --version ${OPENCODE_VERSION} --no-modify-path
ENV PATH="/root/.opencode/bin:${PATH}"

# 5) 컨테이너 안의 git 설정
#    - safe.directory: 윈도우에서 연결(바인드 마운트)한 폴더를 git 이 믿고 쓰게 한다
#    - core.fileMode false: 윈도우 폴더의 "실행 권한" 차이를 변경으로 보지 않게 한다
RUN git config --system --add safe.directory /workspace \
    && git config --system core.fileMode false \
    && git config --system init.defaultBranch main

# 6) 작업 폴더. docker-compose.yml 이 여기에 C 드라이브의 프로젝트 폴더를 연결한다.
WORKDIR /workspace

# 7) 파이썬 패키지 설치 (목록은 requirements.txt)
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# 8) 따로 명령을 주지 않으면 셸을 연다.
CMD ["bash"]
