# modules/gpt_extract_fields.py

from openai import OpenAI
import json

# ✅ OpenAI 클라이언트 생성 함수
def get_client(api_key):
    return OpenAI(api_key=api_key)

# ✅ 입력 유형 분류 함수
def classify_input_type(user_input, api_key):
    client = get_client(api_key)

    system_prompt = """
당신은 지식순환 GPT입니다.

사용자가 건설 프로젝트와 관련된 사례를 자유롭게 입력했습니다.
다음 중 어떤 유형인지 정확히 분류해 주세요:
- 하자사례
- VE사례
- 공사기간
- 기타사례

단순한 인삿말, 질문 등은 '기타사례'로 분류하세요.

형식은 반드시 JSON으로 출력해 주세요:
{
  "type": "하자사례" 또는 "VE사례" 또는 "공사기간" 또는 "기타사례",
  "message": "판단 이유 또는 다음 질문"
}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
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

# ✅ 하자사례 항목 자동 추출 함수
def extract_defect_fields(user_input, api_key):
    client = get_client(api_key)

    prompt = f"""
당신은 건설 회사를 위한 사례 입력 도우미 GPT입니다.

아래 사용자의 설명은 하자사례입니다.
이 내용을 분석하여 다음 항목들을 JSON 형식으로 정리해 주세요.
가능한 경우 빈칸 없이 추론해서 채워 주세요.

출력 예시:
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

사용자 입력:
{user_input}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        content = response.choices[0].message.content
        return json.loads(content.strip())
    except Exception as e:
        return {"error": str(e)}
