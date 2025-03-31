from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# 요청 데이터 모델 정의
class NumberRequest(BaseModel):
    number: int

class TextRequest(BaseModel):
    text: str

# 숫자 처리 엔드포인트
@app.post("/process_number")
async def process_number(request: NumberRequest):
    result = request.number * 2  # 예시로 입력 숫자의 2배를 반환
    print(f"받은 숫자: {request.number}, 반환할 숫자: {result}")  # 디버깅용 출력
    return {"result": result}

# 영문 문장 처리 엔드포인트
@app.post("/process_english")
async def process_english(request: TextRequest):
    response = f"Processed English text: {request.text.upper()}"  # 예시로 대문자로 변환
    print(f"받은 영문: {request.text}")  # 디버깅용 출력
    print(f"반환할 텍스트: {response}")
    return {"result": response}

# 한글 처리 엔드포인트
@app.post("/process_korean")
async def process_korean(request: TextRequest):
    response = f"처리된 한글: {request.text}"  # 예시 응답
    print(f"받은 한글: {request.text}")  # 디버깅용 출력
    print(f"반환할 텍스트: {response}")
    return {"result": response}

if __name__ == "__main__":
    # 모든 IP에서 접근 가능하도록 host를 "0.0.0.0"으로 설정
    uvicorn.run(app, host="0.0.0.0", port=8000)