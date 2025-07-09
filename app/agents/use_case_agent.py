from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI


def get_use_cases_chain() -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["input"],
        template="""
You're a solutions consultant. Extract 3 business use cases from the input.

Each use case should include:
- Title
- Problem Statement
- Solution Provided
- Expected Impact

Respond as list:
[
  {{
    "title": "",
    "problem": "",
    "solution": "",
    "impact": ""
  }},
  ...
]

Input:
{input}
"""
    )
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    return LLMChain(prompt=prompt, llm=llm)
