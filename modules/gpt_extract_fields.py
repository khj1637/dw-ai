# modules/gpt_extract_fields.py

import openai

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

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    try:
        content = response.choices[0].message["content"]
        result = eval(content.strip())  # 안전하게 하려면 json.loads() 방식도 가능
        return result
    except Exception as e:
        return {"error": str(e)}
