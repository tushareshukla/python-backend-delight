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
                "personas": [],
                "error": f"JSON parse failed: {str(e)}",
                "raw_output": raw_output.get("text", str(raw_output))
            }


def get_customer_personas_chain() -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["input"],
        template="""
You're a B2B marketing analyst. Based on the content below, identify 5–6 ideal customer personas.

Each persona should have:
- Persona Name
- Role/Title
- Pain Points
- What They’re Looking For

Respond in JSON format as a list:
[
  {{
    "persona": "Digital Marketer",
    "title": "CMO or Marketing Manager",
    "pain_points": "...",
    "goals": "..."
  }},
  ...
]

Input:
{input}
"""
    )
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    return JSONSafeLLMChain(prompt=prompt, llm=llm)
