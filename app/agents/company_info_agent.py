from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI


def get_company_info_chain() -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["input"],
        template="""
You are a B2B research assistant.

From the input below, extract:
- Company Name
- Industry
- Location (City, Country)
- Value Proposition (summary)
- Target Customers

Respond in this JSON format:
{{
  "company_name": "",
  "industry": "",
  "location": "",
  "value_proposition": "",
  "target_customers": ""
}}

Input:
{input}
"""
    )
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    return LLMChain(prompt=prompt, llm=llm)
