from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI


def get_customer_personas_chain() -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["input"],
        template="""
You're a B2B marketing analyst. Based on the content below, identify 2–3 ideal customer personas.

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
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    return LLMChain(prompt=prompt, llm=llm)
