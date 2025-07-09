from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI


def get_product_details_chain() -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["input"],
        template="""
You're a product analyst. From the input, extract:

- Product/Service Name
- Features (as list)
- Benefits (as list)
- Differentiators

Respond as JSON:
{{
  "product_name": "",
  "features": ["", ""],
  "benefits": ["", ""],
  "differentiators": ""
}}

Input:
{input}
"""
    )
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    return LLMChain(prompt=prompt, llm=llm)
