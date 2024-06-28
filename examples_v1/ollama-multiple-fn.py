import random

def get_weather_forecast(location: str) -> dict[str, str]:
    """Retrieves the weather forecast for a given location"""
    # Mock values for test
    return {
        "location": location,
        "forecast": "sunny",
        "temperature": "25°C",
    }

def get_random_city() -> str:
    """Retrieves a random city from a list of cities"""
    cities = ["Groningen", "Enschede", "Amsterdam", "Istanbul", "Baghdad", "Rio de Janeiro", "Tokyo", "Kampala"]
    return random.choice(cities)

def get_random_number() -> int:
    """Retrieves a random number"""
    # Mock value for test
    return 31

def pyarr_sonarr(python_code: str) -> str:
    """This """
    from pyarr import SonarrAPI
    sonarr = SonarrAPI(base_url='http://192.168.8.17:8989/api/v1/', api_key='ollama')
    return sonarr.execute(python_code)

import inspect

class FunctionCaller:
    """
    A class to call functions from tools.py.
    """

    def __init__(self):
        # Initialize the functions dictionary
        self.functions = {
            "get_weather_forecast": get_weather_forecast,
            "get_random_city": get_random_city,
            "get_random_number": get_random_number,
            "pyarr_sonarr": pyarr_sonarr,
        }
        self.outputs = {}

    def create_functions_metadata(self) -> list[dict]:
        """Creates the functions metadata for the prompt. """
        def format_type(p_type: str) -> str:
            """Format the type of the parameter."""
            # If p_type begins with "<class", then it is a class type
            if p_type.startswith("<class"):
                # Get the class name from the type
                p_type = p_type.split("'")[1]
            
            return p_type
            
        functions_metadata = []
        i = 0
        for name, function in self.functions.items():
            i += 1
            descriptions = function.__doc__.split("\n")
            print(descriptions)
            functions_metadata.append({
                "name": name,
                "description": descriptions[0],
                "parameters": {
                    "properties": [ # Get the parameters for the function
                        {   
                            "name": param_name,
                            "type": format_type(str(param_type)),
                        }
                        # Remove the return type from the parameters
                        for param_name, param_type in function.__annotations__.items() if param_name != "return"
                    ],
                    
                    "required": [param_name for param_name in function.__annotations__ if param_name != "return"],
                } if function.__annotations__ else {},
                "returns": [
                    {
                        "name": name + "_output",
                        "type": {param_name: format_type(str(param_type)) for param_name, param_type in function.__annotations__.items() if param_name == "return"}["return"]
                    }
                ]
            })

        return functions_metadata

    def call_function(self, function):
        """
        Call the function from the given input.

        Args:
            function (dict): A dictionary containing the function details.
        """
    
        def check_if_input_is_output(input: dict) -> dict:
            """Check if the input is an output from a previous function."""
            for key, value in input.items():
                if value in self.outputs:
                    input[key] = self.outputs[value]
            return input

        # Get the function name from the function dictionary
        function_name = function["name"]
        
        # Get the function params from the function dictionary
        function_input = function["params"] if "params" in function else None
        function_input = check_if_input_is_output(function_input) if function_input else None
    
        # Call the function from tools.py with the given input
        # pass all the arguments to the function from the function_input
        output = self.functions[function_name](**function_input) if function_input else self.functions[function_name]()
        self.outputs[function["output"]] = output
        return output

# Initialize the FunctionCaller 
function_caller = FunctionCaller()

# Create the functions metadata
functions_metadata = function_caller.create_functions_metadata()

import json

# Create the system prompt
prompt_beginning = """
You are an AI assistant that can help the user with a variety of tasks. You have access to the following functions:

"""

system_prompt_end = """

When the user asks you a question, if you need to use functions, provide ONLY the label <function_calls> followed by the function calls, and NOTHING ELSE, in the format:
<function_calls>    
[
    { "name": "function_name_1", "params": { "param_1": "value_1", "param_2": "value_2" }, "output": "The output variable name, to be possibly used as input for another function},
    { "name": "function_name_2", "params": { "param_3": "value_3", "param_4": "output_1"}, "output": "The output variable name, to be possibly used as input for another function"},
    ...
]
"""
system_prompt = prompt_beginning + f"<tools> {json.dumps(functions_metadata, indent=4)} </tools>" + system_prompt_end

# Compose the prompt 
user_query = "Do I have the latest season of You downloaded?"
# user_query = "Can you get me the weather forecast for a random city?"


# Get the response from the model
# model_name = 'adrienbrault/nous-hermes2pro:Q8_0'
model_name = 'interstellarninja/hermes-2-theta-llama-3-8b:latest'
base_url = 'http://192.168.8.17:8080/v1/'

# llm = Ollama(model=model_name, base_url=base_url)

from openai import OpenAI

client = OpenAI(
    base_url=base_url,
    api_key="ollama",
)



messages = [
    {'role': 'system', 'content': system_prompt,
    },
    {'role': 'user', 'content': user_query}
]
# response = ollama.chat(model=model_name, messages=messages)
i = 1
max_attempts = 20

while i <= max_attempts:
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.1,
        # response_format={'type': 'json_object'}
    )

# response = llm.invoke(messages)

# print(f"messages before response:\n{messages}") #! debugging
# response = Ollama(model=model_name, base_url=base_url).invoke(messages)


# Ollama(model=model_name, base_url=base_url).generate()

    print(response)
# Get the function calls from the response
# function_calls = response["message"]["content"]


    function_calls = response.choices[0].message.content
    # If it ends with a <function_calls>, get everything before it
    if function_calls.startswith("<function_calls>"):
        function_calls = function_calls.split("<function_calls>")[1]

# Read function calls as json
    try:
        function_calls_json: list[dict[str, str]] = json.loads(function_calls)
        redo_completion = False
    except json.JSONDecodeError:
        print(function_calls)
        function_calls_json = []
        print (f"Attempt {i}/{max_attempts}: Model response not in desired JSON format")
        redo_completion = True
    finally:
        print("Function calls:")
        print(function_calls_json)
    
    if redo_completion == False:
        break
    else:
        i += 1
        continue
    
    
# Call the functions
output = ""
for function in function_calls_json:
    output = f"Agent Response: {function_caller.call_function(function)}"

print(output)

