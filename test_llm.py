import litellm
from dotenv import load_dotenv
load_dotenv()

response = litellm.completion(
    model="openrouter/anthropic/claude-3-haiku",
    messages=[{"role": "user", "content": "Write a simple Python function to say 'Hello, World!'"}]
)
print(response.choices[0].message.content)
