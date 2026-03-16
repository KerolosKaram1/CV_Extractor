from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

response = client.chat.completions.create(
    model="stepfun/step-3.5-flash:free",
    messages=[
        {"role": "user", "content": "Say hello"}
    ]
)

print(response)