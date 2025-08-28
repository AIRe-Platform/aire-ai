# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import uuid
from datetime import datetime, timezone
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import PromptTemplate
from aire.models.questionnaire import *
from llm import DefaultModel

summarizy_prompt_template = """
Please summarize the following facts:
{text}
"""

def __build_prompt(item: AireQuestionnaireAnswer):
    answer = item.answer
    if type(answer) is list:
        answer = ", ".join(answer)

    if item.prompt and item.options:
        if type(answer) is dict[str, Any]:
            return item.prompt.format(question=item.question, **answer, **item.options)
        else:
            return item.prompt.format(answer=answer, question=item.question, **item.options)
    else:
        return ""

def __process_questionnaire(input: AireQuestionnaireProcessingRequest) -> AireQuestionnaireResult:
    prompts_to_process = filter(lambda x: x.prompt != None and x.answer != None, input.answers)
    prompts = list(map(__build_prompt, prompts_to_process))
    llm = DefaultModel(temperature=0.0)
    summary = None

    if len(prompts) > 0:
        summary_prompt = PromptTemplate.from_template(summarizy_prompt_template)
        summary_chain = summary_prompt | llm
        summary_result = summary_chain.invoke({ "text": "\n".join(prompts) })
        summary = summary_result.content

    if summary is not str:
        summary = "No summary available."

    return AireQuestionnaireResult(
        id=str(uuid.uuid4()),
        questionnaire_id=input.questionnaire_id, 
        timestamp=datetime.now(timezone.utc),
        answers=input.answers,
        summary=summary,
        prompts=prompts)


ProcessQuestionnaireChain = RunnableLambda(__process_questionnaire)
