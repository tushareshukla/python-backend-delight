from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI


def get_event_details_chain() -> LLMChain:
    prompt = PromptTemplate(
        input_variables=["input"],
        template="""
You are an event strategist. From the input, extract:

- Event Name
- Event Type (webinar, summit, etc.)
- Date (if available)
- Audience
- Agenda/Topics

Respond as:
{{
  "event_name": "",
  "event_type": "",
  "date": "",
  "audience": "",
  "topics": ["", ""]
}}

Input:
{input}
"""
    )
    llm = ChatOpenAI(temperature=0, model="gpt-4")
    return LLMChain(prompt=prompt, llm=llm)
