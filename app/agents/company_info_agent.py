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
                "company_name": "",
                "description": "",
                "error": f"JSON parse failed: {str(e)}",
                "raw_output": raw_output["text"] if "text" in raw_output else str(raw_output)
            }


def get_company_info_chain() -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["input"],
        template="""
You are a research assistant.

From the input below, extract:
- Company Name
- A short 2-3 sentence company description (what it does, whom it serves, and how)

Respond in this JSON format:
{{
  "company_name": "",
  "description": ""
}}

Input:
{input}
"""
    )

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    return JSONSafeLLMChain(prompt=prompt, llm=llm)
