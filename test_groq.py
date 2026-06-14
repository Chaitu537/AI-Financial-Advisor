from groq import Groq

client = Groq(
    api_key="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"

)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": "What is SIP?"
        }
    ]
)

print(response.choices[0].message.content)
