각 폴더가 하나의 프로젝트로 취급되서 동작 할 예정 !

python -m venv dev-env

dev-env\Scripts\activate.bat

pip install -r requirements.txt

pip freeze > requirements.txt

python convert_requirements.py


### 모든 패키지 삭제

pip freeze > all_packages.txt
pip uninstall -r all_packages.txt -y
del all_packages.txt

## 다시 전체 설치
pip install -r requirements.txt