import json
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI


class JSONSafeLLMChain(LLMChain):
    def invoke(self, input):
        raw_output = super().invoke(input)
        try:
            return json.loads(raw_output["text"])
        except Exception as e:
            return {
                "use_cases": [],
                "error": f"JSON parse failed: {str(e)}",
                "raw_output": raw_output.get("text", str(raw_output))
            }


def get_use_cases_chain() -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["input"],
        template="""
You're a solutions consultant. Extract 4 business use cases from the input.

Each use case should include:
- Title
- Problem Statement
- Solution Provided
- Expected Impact

Respond as list:
[
  {{
    "title": "Use Case Title",
    "problem": "Brief problem statement...",
    "solution": "How this solves the problem...",
    "impact": "Expected benefit or impact..."
  }},
  ...
]

Input:
{input}
"""
    )
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    return JSONSafeLLMChain(prompt=prompt, llm=llm)
