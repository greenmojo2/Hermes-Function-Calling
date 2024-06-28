import openai
import os

# Set the OPENAI_API_KEY environment variable
os.environ['OPENAI_API_KEY'] = 'localai-api-key'

# Set the OPENAI_API_BASE environment variable
#os.environ['OPENAI_API_BASE'] = 'http://192.168.57.92:8080/' #from wsl linux
os.environ['OPENAI_API_BASE'] = 'http://192.168.8.17:8080/v1' #'http://localhost:8080/'


# Verify that the environment variables are set
print("OPENAI_API_KEY:", os.environ.get('OPENAI_API_KEY'))
print("OPENAI_API_BASE:", os.environ.get('OPENAI_API_BASE'))

# Send the conversation and available functions to GPT
messages = [{"role": "user", "content": "What's the weather like in Boston?"}]
functions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    }
]

openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.api_base = os.environ.get("OPENAI_API_BASE")

response = openai.ChatCompletion.create(
    model="interstellarninja/hermes-2-theta-llama-3-8b:latest", #"Hermes-2-Pro-Llama-3-8B-Q5_K_M.gguf",
    messages=messages,
    functions=functions,
    tool_choice="auto"
)

print(response.choices[0].message["content"])