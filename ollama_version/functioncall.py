import argparse
import json
from langchain_community.llms import Ollama

import functions
from prompter import PromptManager
from validator import validate_function_call_schema
from utils import (
    print_nous_text_art,
    inference_logger,
    get_assistant_message,
    get_chat_template,
    validate_and_extract_tool_calls
)

llama3 = Ollama(model='llama3:latest')
class ModelInference:
    def __init__(self, chat_template):
        inference_logger.info(print_nous_text_art())
        self.prompter = PromptManager()
        self.ollama_client = llama3
        self.chat_template = get_chat_template(chat_template)

    def run_inference(self, prompt):
        inputs = self.ollama_client.apply_chat_template(
            prompt,
            add_generation_prompt=True,
            return_tensors='pt'
        )
        tokens = self.ollama_client.generate(
            inputs,
            max_new_tokens=1500,
            temperature=0.8,
            repetition_penalty=1.1,
            do_sample=True,
            eos_token_id=self.ollama_client.tokenizer.eos_token_id
        )
        completion = self.ollama_client.tokenizer.decode(tokens[0], skip_special_tokens=False, clean_up_tokenization_space=True)
        return completion

    def process_completion_and_validate(self, completion, chat_template):
        assistant_message = get_assistant_message(completion, chat_template, self.ollama_client.tokenizer.eos_token)
        if assistant_message:
            validation, tool_calls, error_message = validate_and_extract_tool_calls(assistant_message)
            if validation:
                inference_logger.info(f"parsed tool calls:\n{json.dumps(tool_calls, indent=2)}")
                return tool_calls, assistant_message, error_message
            else:
                return None, assistant_message, error_message
        else:
            inference_logger.warning("Assistant message is None")
            raise ValueError("Assistant message is None")

    def execute_function_call(self, tool_call):
        function_name = tool_call.get("name")
        function_to_call = getattr(functions, function_name, None)
        function_args = tool_call.get("arguments", {})
        inference_logger.info(f"Invoking function call {function_name} ...")
        function_response = function_to_call(*function_args.values())
        results_dict = f'{{"name": "{function_name}", "content": {function_response}}}'
        return results_dict

    def generate_function_call(self, query, chat_template, num_fewshot, max_depth=5):
        try:
            depth = 0
            user_message = f"{query}\nThis is the first turn and you don't have <tool_results> to analyze yet"
            chat = [{"role": "user", "content": user_message}]
            tools = functions.get_openai_tools()
            prompt = self.prompter.generate_prompt(chat, tools, num_fewshot)
            completion = self.run_inference(prompt)

            def recursive_loop(prompt, completion, depth):
                nonlocal max_depth
                tool_calls, assistant_message, error_message = self.process_completion_and_validate(completion, chat_template)
                prompt.append({"role": "assistant", "content": assistant_message})

                if tool_calls:
                    for tool_call in tool_calls:
                        validation, message = validate_function_call_schema(tool_call, tools)
                        if validation:
                            try:
                                function_response = self.execute_function_call(tool_call)
                                prompt.append({"role": "tool", "content": function_response})
                                inference_logger.info(f"Function response: {function_response}")
                            except Exception as e:
                                inference_logger.error(f"Could not execute function: {e}")
                        else:
                            inference_logger.error(message)

                    depth += 1
                    if depth >= max_depth:
                        print(f"Maximum recursion depth reached ({max_depth}). Stopping recursion.")
                        return

                    completion = self.run_inference(prompt)
                    recursive_loop(prompt, completion, depth)
                elif error_message:
                    inference_logger.error(f"Error parsing function calls: {error_message}")

            recursive_loop(prompt, completion, depth)

        except Exception as e:
            inference_logger.error(f"Exception occurred: {e}")
            raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run recursive function calling loop")
    parser.add_argument("--chat_template", type=str, default="chatml", help="Chat template for prompt formatting")
    parser.add_argument("--num_fewshot", type=int, default=None, help="Option to use json mode examples")
    parser.add_argument("--query", type=str, default="I need the current stock price of Tesla (TSLA)")
    parser.add_argument("--max_depth", type=int, default=5, help="Maximum number of recursive iteration")
    args = parser.parse_args()

    inference = ModelInference(args.chat_template)
    inference.generate_function_call(args.query, args.chat_template, args.num_fewshot, args.max_depth)