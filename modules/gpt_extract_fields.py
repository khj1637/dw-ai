from openai import OpenAI
import json

# ✅ 클라이언트 생성
def get_client(api_key):
    return OpenAI(api_key=api_key)

# ✅ 하자사례 항목 자동 추출 함수
def extract_defect_fields(user_input, api_key):
    client = get_client(api_key)

    prompt = f"""
당신은 건설 회사의 사례 등록을 돕는 AI 어시스턴트입니다.

다음 사용자 입력은 하자사례에 대한 설명입니다. 이 내용을 분석하여 아래 항목별로 분류해 주세요.

입력:
{user_input}

출력 형식은 반드시 JSON이며, 가능한 한 빈 칸 없이 추론해서 채워주세요.

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
            model="gpt-4",  # 또는 "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        content = response.choices[0].message.content
        return json.loads(content.strip())  # 보안상 eval 대신 json.loads 사용
    except Exception as e:
        return {"error": str(e)}

# ✅ 입력 유형 분류 함수 (하자사례 / VE사례 / 공사기간 / 기타)
def classify_input_type(user_input, api_key):
    client = get_client(api_key)

    system_prompt = """
당신은 지식순환 GPT입니다.

아래 사용자 입력을 읽고 다음 중 하나로 정확하게 분류해 주세요:
- 하자사례
- VE사례
- 공사기간
- 기타사례

단순한 인삿말이나 질문일 경우 '기타사례'로 분류하고, 가능한 경우에는 대화를 자연스럽게 이어가도록 유도할 수 있는 메시지도 작성해주세요.

반드시 JSON 형식으로 출력하세요:
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
