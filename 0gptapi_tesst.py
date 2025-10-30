from openai import OpenAI
from dotenv import load_dotenv
import os

# 환경변수 로딩
load_dotenv(override=True)

# 메모리에 로딩된 값을 api_key 변수에 대입
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# print(api_key)

# OpenAI 객체 생성
client = OpenAI(api_key=OPENAI_API_KEY)

# 챗 컴플리션 실행
completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "너는 IT전문가야."},
    {"role": "user", "content": "전세계서 가장 많이 사용하는 프로그래밍 언어 top5를 얘기해줘"}
  ]
)

print(completion.choices[0].message.content)