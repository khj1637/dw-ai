import openai

# ✅ 1. 하자사례 항목 자동 추출 함수
def extract_defect_fields(user_input, api_key):
    openai.api_key = api_key

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
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        content = response.choices[0].message["content"]
        result = eval(content.strip())  # ⚠️ 운영 시에는 json.loads 권장
        return result
    except Exception as e:
        return {"error": str(e)}

# ✅ 2. 사용자 입력 분류 함수 (하자사례 / VE사례 / 일반질문)
def classify_input_type(user_input, api_key):
    openai.api_key = api_key

    system_prompt = """
당신은 지식순환 시스템을 위한 분류 전문가입니다.
사용자의 자연어 입력을 아래의 세 가지 유형 중 하나로 분류해 주세요:
- 하자사례
- VE사례
- 일반 질문 (저장 불필요)

그리고 해당 판단에 대한 간단한 이유나 요약도 함께 주세요.

출력은 반드시 JSON 형식으로 반환해 주세요:
{
  "type": "하자사례" 또는 "VE사례" 또는 "일반 질문",
  "message": "이유나 간단 요약"
}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3
        )
        content = response.choices[0].message["content"]
        result = eval(content.strip())  # ⚠️ 보안 강화를 위해 json.loads 권장
        return result
    except Exception as e:
        return {"type": "오류", "message": str(e)}
