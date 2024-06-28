from openai import OpenAI
from pydantic import BaseModel
import instructor

#* my addition for organization
def print_separator():
    # print("\n")
    print("*"*80)
    # print("\n")
    

class UserDetail(BaseModel):
    name: str
    age: int


# enables `response_model` in create call
client = instructor.patch(
    OpenAI(
        base_url="http://192.168.8.17:8080/v1", #"http://localhost:11434/v1",
        api_key="ollama",  # required, but unused
    ),
    mode=instructor.Mode.JSON,
)

user = client.chat.completions.create(
    model="interstellarninja/hermes-2-theta-llama-3-8b:latest", #"adrienbrault/nous-hermes2pro:Q8_0",
    messages=[
        {
            "role": "user",
            "content": "Jason is 30 years old",
        }
    ],
    response_model=UserDetail,
)

print(user)
#> name='Jason' age=30

print_separator()

### synthatitc data
from typing import Iterable

def generate_fake_users(count: int) -> Iterable[UserDetail]:
    return client.chat.completions.create(
        model="interstellarninja/hermes-2-theta-llama-3-8b:latest",
        response_model=Iterable[UserDetail],
        messages=[
            {"role": "user", "content": f"Generate a {count} synthetic users"},
        ],
    )


for user in generate_fake_users(5):
    print(user)
    
print_separator()

from typing import List
class QuestionAnswer(BaseModel):
    question: str
    answer: str
    citations: List[str]
# QuestionAnswer.model_json_schema() # i had to change this to below
print(QuestionAnswer.model_json_schema())

print_separator()

def ask_ai(question: str, context: str) -> QuestionAnswer:
    return client.chat.completions.create(
        model="interstellarninja/hermes-2-theta-llama-3-8b:latest", #"adrienbrault/nous-hermes2pro:Q8_0",
        temperature=0.1,
        response_model=QuestionAnswer,
        messages=[
            {
                "role": "system",
                "content": "You are a world class algorithm to answer questions with correct and exact citations.",
            },
            {"role": "user", "content": f"{context}"},
            {"role": "user", "content": f"Question: {question}"},
        ],
        validation_context={"text_chunk": context},
    )
    
question = "What did the author do during college?"
context = """
My name is Jason Liu, and I grew up in Toronto Canada but I was born in China.
I went to an arts high school but in university I studied Computational Mathematics and physics.
As part of coop I worked at many companies including Stitchfix, Facebook.
I also started the Data Science club at the University of Waterloo and I was the president of the club for 2 years.
"""

response = ask_ai(question, context)
print(response.answer)
print(response.citations)

print_separator()

question1 = "Where was John born?"
context1 = """
John Doe is a software engineer who was born in New York, USA. 
He studied Computer Science at the Massachusetts Institute of Technology. 
During his studies, he interned at Google and Microsoft. 
He also founded the Artificial Intelligence club at his university and served as its president for three years.
"""


question2 = "What did Emily study in university?"
context2 = """
Emily Smith is a data scientist from London, England. 
She attended the University of Cambridge where she studied Statistics and Machine Learning. 
She interned at IBM and Amazon during her summer breaks. 
Emily was also the head of the Women in Tech society at her university.
"""

question3 = "Which companies did Robert intern at?"
context3 = """
Robert Johnson, originally from Sydney, Australia, is a renowned cybersecurity expert. 
He studied Information Systems at the University of Melbourne. 
Robert interned at several cybersecurity firms including NortonLifeLock and McAfee. 
He was also the leader of the Cybersecurity club at his university.
"""


question4 = "What club did Alice start at her university?"
context4 = """
Alice Williams, a native of Dublin, Ireland, is a successful web developer. 
She studied Software Engineering at Trinity College Dublin. 
Alice interned at several tech companies including Shopify and Squarespace. 
She started the Web Development club at her university and was its president for two years.
"""


question5 = "What did Michael study in high school?"
context5 = """
Michael Brown is a game developer from Tokyo, Japan. 
He attended a specialized high school where he studied Game Design. 
He later attended the University of Tokyo where he studied Computer Science. 
Michael interned at Sony and Nintendo during his university years. 
He also started the Game Developers club at his university.
"""

for question, context in [
    (question1, context1),
    (question2, context2),
    (question3, context3),
    (question4, context4),
    (question5, context5),
]:
    response = ask_ai(question, context)
    print(question)
    print(response.answer)
    print(response.citations)
    print("\n\n")