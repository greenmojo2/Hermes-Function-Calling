from openai import OpenAI
from pydantic import BaseModel
import instructor
import json
from typing import List

# enables `response_model` in create call
client = instructor.patch(
    OpenAI(
        base_url="http://192.168.8.17:8080/v1", #"http://localhost:11434/v1",
        api_key="ollama",  # required, but unused
    ),
    mode=instructor.Mode.JSON,
)



class Citation(BaseModel):
    source: str
    details: str  # or any other fields that are expected

class QuestionAnswer(BaseModel):
    question: str
    answer: str
    citations: List[Citation]
QuestionAnswer.model_json_schema()

def ask_agent(question: str, context: str) -> QuestionAnswer:
    messages=[
            {
                "role": "system",
                "content": "You are a world class agentic framework to answer questions with correct and exact citations.",
            },
            {"role": "user", "content": f"{context}"},
            {"role": "user", "content": f"Question: {question}"},
        ]
    return client.chat.completions.create(
        model="interstellarninja/hermes-2-theta-llama-3-8b:latest", #model="adrienbrault/nous-hermes2pro:Q4_0",
        temperature=0.1,
        response_model=QuestionAnswer,
        messages=messages,
    )
    
# from typing import List
class SelfReflection(BaseModel):
    scratchpad: str
    sub_questions: List[str]
SelfReflection.model_json_schema()

#* so far so good

from concurrent.futures import ThreadPoolExecutor

def ask_ai(question: str) -> SelfReflection:
    messages=[
            {
                "role": "system",
                "content": "You are a world class agentic framework to decompose a given question into 5 sub-questions to help collect evidences for final answer. You must plan your query step-by-step inside the <scratchpad></scratchpad> tags",
            },
            {"role": "user", "content": f"{question}"},
        ]
    return client.chat.completions.create(
        model="interstellarninja/hermes-2-theta-llama-3-8b:latest", #model="adrienbrault/nous-hermes2pro:Q4_0",
        temperature=0.1,
        response_model=SelfReflection,
        messages=messages,
    ), messages

def self_reflection_loop(question: str) -> QuestionAnswer:
    response, messages = ask_ai(question)
    
    agent_calls = ""
    for query in response.sub_questions:
        agent_calls += f"<agent>\n{query}\n</agent>\n"

    content = f"<scratchpad> {response.scratchpad} </scratchpad>\n"
    content += agent_calls
    messages.append({
        "role": "assistant",
        "content": content
    })

    context = ""

    with ThreadPoolExecutor() as executor:
        futures = []

        for query in response.sub_questions:
            future = executor.submit(ask_agent, query, context)
            futures.append(future)

        agent_messages = [] 
        for i in range(len(futures)):
            result = futures[i].result()

            agent_messages.append(
                {
                    "role": f"agent-{i}",
                    "content": response.sub_questions[i]
                }
            )
            agent_messages.append(
                {
                    "role": f"agent-{i}-response",
                    "content": result.answer
                }
            )
            context += f"<agent id={i}>\n"
            context += f"sub_query: {response.sub_questions[i]}\n"
            context += f"answer: {result.answer}\n"
            context += f"</agent>\n"
    print(context)
    messages.append({
        "role": "agents",
        "content": agent_messages
    })
    final_answer = ask_agent(question, context)
    messages.append({
        "role": "assistant",
        "content": final_answer.answer
    })
    return final_answer, messages


question = "Who is Jay Gatsby?"
response, messages = self_reflection_loop(question)
# exit()
# response.answer
print(messages)
print(json.dumps(messages, indent=2))