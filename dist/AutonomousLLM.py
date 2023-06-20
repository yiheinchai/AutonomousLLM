# AUTOGENERATED! DO NOT EDIT! File to edit: ../AutonomousLLM.ipynb.

# %% auto 0
__all__ = ['auto_llm', 'Utils', 'CallGuard', 'AutonomousLLM']

# %% ../AutonomousLLM.ipynb 1
import random
import os
import openai
import inspect
import types
import re
import textwrap
import guardrails as gd
from rich import print
from dotenv import load_dotenv
from ast import literal_eval
import json
import nbdev

# %% ../AutonomousLLM.ipynb 2
load_dotenv()

# %% ../AutonomousLLM.ipynb 9
class Utils:
    def __init__(self):
        pass

    def is_builtin(self, obj):
        """Check if an object is a built-in function or method."""
        if isinstance(obj, types.BuiltinFunctionType) or isinstance(
            obj, types.BuiltinMethodType
        ):
            return True
        return False

    def inspect_methods(self, obj):
        """Print the methods and code implementation of an object."""
        output_string = ""

        methods = inspect.getmembers(obj, inspect.ismethod)
        for name, method in methods:
            if not self.is_builtin(method):
                output_string += inspect.getsource(method) + "\n"

        dedented_code = textwrap.dedent(output_string)
        return dedented_code

    def convert_string_to_dict(self, string):
        cleaned_string = string.replace('\n', '')
        dictionary = json.loads(cleaned_string)
        return dictionary

# %% ../AutonomousLLM.ipynb 10
class CallGuard:

    def __init__(self) -> None:
        pass

    def _guard_call_api(self, guard, params={}):
        raw_llm_response, validated_response = guard(
            openai.ChatCompletion.create,
            prompt_params=params,
            model="gpt-3.5-turbo",
            max_tokens=2048,
            temperature=0,
        )

        print(raw_llm_response)

        return validated_response

    def generate_code_given_task(self, task):
        guard = gd.Guard.from_rail("./rail/code_gen.xml")
        return self._guard_call_api(guard, {"prompt": task})
     
    def generate_ideas(self):
        guard = gd.Guard.from_rail("./rail/idea_gen.xml")
        return self._guard_call_api(guard)
        

# %% ../AutonomousLLM.ipynb 11
class AutonomousLLM(Utils, CallGuard):
    def __init__(self):
        super().__init__()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.ideas = []
        self.methods = []

    def execute_code(self, code):
        # Process the returned code and add it to AutonomousLLM
        exec(code, globals())

    def execute_code_local(self, code):
        # Process the returned code and add it to AutonomousLLM
        exec(code, globals(), locals())

    def add_ability(self, response):
        if new_func := response.get('new_method'):
            self.execute_code(textwrap.dedent(new_func))

        if attach_func := response.get('attach_method'):
            self.execute_code(textwrap.dedent(attach_func))
            self.methods.append(new_func)        

    def run(self, num_calls=500):
        calls_to_make = num_calls
        while calls_to_make > 0:
            calls_to_make -= 1
            # Make an API call to GPT-3.5 Turbo
            if len(self.ideas) < 1:
                self.ideas += self.generate_ideas()['ideas']
                continue
 
            idea = self.ideas.pop(-1)
            print("IDEA:", idea)
            res = self.generate_code_given_task(idea)

            if new_func := res.get('new_method'):
                self.execute_code(textwrap.dedent(new_func))

            if attach_func := res.get('attach_method'):
                self.execute_code_local(textwrap.dedent(attach_func))
                self.methods.append(new_func)



    def use_new_ability(self):
        # Use the newly added ability in your code
        pass

# %% ../AutonomousLLM.ipynb 12
auto_llm = AutonomousLLM()

# %% ../AutonomousLLM.ipynb 13
auto_llm.run()
