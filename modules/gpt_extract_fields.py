from openai import OpenAI
import json

# ✅ 공통 클라이언트 생성 함수
def get_client(api_key):
    return OpenAI(api_key=api_key)

# ✅ 1. 하자사례 항목 자동 추출 함수
def extract_defect_fields(user_input, api_key):
    client = get_client(api_key)

    prompt = f"""
다음은 건설 현장에서 발생한 하자사례입니다. 이 내용을 아래 항목에 맞게 분류해 주세요.

입력 문장:
{user_input}

출력 형식 (JSON 형식):
{{
  "현장명": "",
  "발생일": "",
  "공종": "",
  "사례 결과": "성공사례 또는 실패사례 중 하나",
  "하자 내용": "",
  "상세 내용": "",
  "해결 방안": "",
  "실패 원인": ""
}}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 또는 gpt-4
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        content = response.choices[0].message.content
        return json.loads(content.strip())  # ⚠️ 보안상 eval 대신 json.loads
    except Exception as e:
        return {"error": str(e)}

# ✅ 2. 사용자 입력 분류 함수 (하자사례 / VE사례 / 일반질문)
def classify_input_type(user_input, api_key):
    client = get_client(api_key)

    system_prompt = """
당신은 "지식순환 시스템"의 GPT입니다. 사용자의 자연어 입력을 아래 네 가지 중 하나로 분류해 주세요:

- 하자사례: 건설현장에서 발생한 문제, 하자, 개선사례 등
- VE사례: 설계 또는 시공 개선을 통해 비용 절감, 효율 개선한 사례
- 공사기간: 건축물 또는 공정의 공사기간과 관련된 사례
- 일반 질문: 단순한 인사, 잡담, 앱 사용 문의 등

만약 사용자의 입력이 불완전하거나 정확히 분류하기 어려우면 추가 질문을 통해 정보를 유도하세요.  
너무 단순한 인사말이라면 다음과 같이 안내해 주세요:  
"안녕하세요! 하자사례, VE사례, 공사기간 관련 사례를 입력해 주시면 등록 도와드릴게요 😊"

출력은 반드시 JSON 형식으로 반환해 주세요:

{
  "type": "하자사례" 또는 "VE사례" 또는 "공사기간" 또는 "일반 질문",
  "message": "간단한 판단 이유 또는 유도 메시지"
}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 또는 gpt-4
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3
        )
        content = response.choices[0].message.content
        return json.loads(content.strip())
    except Exception as e:
        return {"type": "오류", "message": str(e)}
