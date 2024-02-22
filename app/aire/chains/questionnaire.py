import datetime, uuid
from langchain.schema.runnable import RunnableLambda
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from ..models.questionnaire import (
    AireQuestionnaireProcessingRequest, 
    AireQuestionnaireResult, 
    AireQuestionnaireAnswer
)
from ..llm import ChatModel

summarizy_prompt_template = """
Please summarize the following facts:
{text}
"""

def __build_prompt(item: AireQuestionnaireAnswer):
    answer = item.answer
    if type(answer) is list:
        answer = ", ".join(answer)

    if type(answer) is dict:
        return item.prompt.format(question=item.question, **answer, **item.options)
    else:
        return item.prompt.format(answer=answer, question=item.question, **item.options)

def __process_questionnaire(input: AireQuestionnaireProcessingRequest) -> AireQuestionnaireResult:
    prompts_to_process = filter(lambda x: x.prompt != None and x.answer != None, input.answers)
    prompts = list(map(__build_prompt, prompts_to_process))

    summary_prompt = PromptTemplate.from_template(summarizy_prompt_template)
    summary_chain = LLMChain(llm=ChatModel(temperature=0.0), prompt=summary_prompt)
    summary = summary_chain.invoke({ "text": "\n".join(prompts) })

    return AireQuestionnaireResult(
        id=str(uuid.uuid4()),
        questionnaire_id=input.questionnaire_id, 
        timestamp=datetime.datetime.utcnow(),
        answers=input.answers,
        summary=summary['text'],
        prompts=prompts)


ProcessQuestionnaireChain = RunnableLambda(__process_questionnaire)
