@echo off

REM 현재 디렉토리를 스택에 푸시
pushd "%~dp0"

REM dev-env 디렉토리로 이동
cd dev-env

REM Scripts 디렉토리로 이동
cd Scripts

REM 가상 환경 활성화
call activate.bat

REM 원래 디렉토리로 복귀
popd

REM app.py 실행
python app.py
