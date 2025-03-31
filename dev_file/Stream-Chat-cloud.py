from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
import requests  # 추가: 직접 HTTP 요청을 위해

# .env 파일 로드
load_dotenv()

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 구체적인 origin을 지정하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# UTF-8 인코딩 미들웨어 추가
@app.middleware("http")
async def add_charset_middleware(request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "text/event-stream; charset=utf-8"
    return response

# API 키를 저장할 변수
current_api_key = os.getenv('OPENAI_API_KEY')

class ChatRequest(BaseModel):
    message: str
    api_key: Optional[str] = None
    conversation_id: Optional[str] = None  # 대화 식별을 위한 ID
    is_continuous: bool = False  # 연속 대화 여부

# 대화 기록을 저장할 딕셔너리
conversations = {}

async def process_direct_stream(response, request):
    """직접 API 응답 스트림을 처리하는 함수"""
    collected_message = []
    
    # requests의 스트림 응답 처리
    for line in response.iter_lines():
        if line:
            # "data: " 접두사로 시작하는 라인만 처리
            line = line.decode('utf-8')
            if line.startswith('data: '):
                if line.strip() == 'data: [DONE]':
                    break
                
                # JSON 파싱
                try:
                    json_str = line[6:]  # "data: " 이후의 문자열
                    data = json.loads(json_str)
                    
                    # 컨텐츠 추출
                    if 'choices' in data and len(data['choices']) > 0:
                        choice = data['choices'][0]
                        if 'delta' in choice and 'content' in choice['delta']:
                            content = choice['delta']['content']
                            collected_message.append(content)
                            
                            # 클라이언트에게 전송
                            yield f"data: {content}\n\n".encode('utf-8')
                            await asyncio.sleep(0.01)
                except Exception as e:
                    print(f"JSON 파싱 오류: {e}")
    
    # 연속 대화일 경우 전체 메시지 저장
    if request.is_continuous and request.conversation_id:
        full_message = ''.join(collected_message)
        if request.conversation_id not in conversations:
            conversations[request.conversation_id] = []
        conversations[request.conversation_id].append({"role": "user", "content": request.message})
        conversations[request.conversation_id].append({
            "role": "assistant",
            "content": full_message
        })

@app.post("/chat")
async def chat_with_gpt(request: ChatRequest):
    try:
        print("요청 받음:", request)  # 디버깅용 로그
        api_key = request.api_key if request.api_key else current_api_key
        
        if not api_key:
            print("API 키 없음")  # 디버깅용 로그
            return {"error": "API 키가 설정되지 않았습니다. API 키를 입력하거나 환경변수를 설정해주세요."}
        
        # 메시지 히스토리 관리
        if request.is_continuous:
            if request.conversation_id not in conversations:
                conversations[request.conversation_id] = []
            messages = conversations[request.conversation_id] + [{"role": "user", "content": request.message}]
        else:
            messages = [{"role": "user", "content": request.message}]
        
        print("메시지 전송 시작:", messages)  # 디버깅용 로그
        
        # 직접 OpenAI API 호출 (라이브러리 우회)
        try:
            # API 요청 데이터 준비
            api_url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            # ASCII 이스케이프 문자로 변환
            safe_messages = []
            for msg in messages:
                # 컨텐츠를 ASCII로 안전하게 변환
                safe_content = json.dumps(msg["content"], ensure_ascii=True)
                # 따옴표 제거 (JSON 덤프가 추가함)
                safe_content = safe_content[1:-1]
                safe_messages.append({"role": msg["role"], "content": safe_content})
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": safe_messages,
                "stream": True
            }
            
            # JSON 직접 덤핑 (ensure_ascii=True)
            json_data = json.dumps(data, ensure_ascii=True)
            
            print("직접 API 호출 (ASCII 변환됨)")
            
            # 요청 전송 (스트리밍 모드)
            response = requests.post(
                api_url,
                headers=headers,
                data=json_data,  # 직접 JSON 문자열 전달
                stream=True
            )
            
            if response.status_code != 200:
                error_msg = f"API 오류: {response.status_code} - {response.text}"
                print(error_msg)
                return {"error": error_msg}
            
            print("API 응답 받음, 스트리밍 시작")
            
            return StreamingResponse(
                process_direct_stream(response, request), 
                media_type='text/event-stream',
                headers={
                    'Content-Type': 'text/event-stream; charset=utf-8',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                }
            )
            
        except Exception as e:
            print(f"API 직접 호출 중 오류: {str(e)}")
            raise e
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")  # 디버깅용 로그
        error_str = str(e)
        if "invalid_api_key" in error_str:
            return {"error": "잘못된 API 키입니다. OpenAI 웹사이트에서 올바른 API 키를 확인해주세요."}
        elif "insufficient_quota" in error_str:
            return {"error": "API 키의 사용량이 초과되었습니다. 결제 정보를 확인해주세요."}
        elif "invalid_request_error" in error_str:
            return {"error": "잘못된 요청입니다. 입력값을 확인해주세요."}
        else:
            return {"error": f"서버에서 오류가 발생했습니다: {str(e)}"}
            
@app.delete("/chat/{conversation_id}")
async def clear_chat_history(conversation_id: str):
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "대화 기록이 삭제되었습니다."}
    return {"message": "해당 대화 기록이 존재하지 않습니다."}

# 서버가 모든 IP(0.0.0.0)에서 접근을 허용
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
