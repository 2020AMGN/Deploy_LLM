#!/bin/bash
# 권한등록 : chmod +x activate_run.sh

# 현재 스크립트가 있는 디렉토리를 저장
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 가상 환경 경로를 절대 경로로 설정
VENV_PATH="$DIR/dev-env/bin/activate"

# 현재 디렉토리를 스택에 푸시
pushd "$DIR" > /dev/null

# 가상 환경 활성화
source "$VENV_PATH"

# app.py 실행
python "$DIR/app.py"

# 스크립트가 있는 디렉토리로 복귀
popd DIR
