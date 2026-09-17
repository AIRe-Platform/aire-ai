# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import uuid
from datetime import datetime, timezone
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import PromptTemplate
from aire.models.questionnaire import *
from utils.auth import AireAuth
from llm import DefaultModel

summarizy_prompt_template = """
Please summarize the following facts:
{text}
"""

question_answer_template = """
Question: {question}
Answer: {answer}
"""

class QuestionnaireChainInput(BaseModel):
    req: AireQuestionnaireProcessingRequest
    auth: AireAuth

def __build_prompt(item: AireQuestionnaireAnswer):
    answer = item.answer
    if isinstance(answer, list):
        answer = ", ".join(answer)

    if item.prompt and item.options:
        try:
            if isinstance(answer, dict):
                return item.prompt.format(question=item.question, **answer, **item.options)
            else:
                return item.prompt.format(answer=answer, question=item.question, **item.options)
        except:
            pass
    
    # Fallback to default prompt template
    return question_answer_template.format(question=item.question, answer=answer)

async def __process_questionnaire(input: QuestionnaireChainInput) -> AireQuestionnaireResult:
    prompts_to_process = filter(lambda x: x.prompt != None and x.answer != None, input.req.answers)
    prompts = list(map(__build_prompt, prompts_to_process))
    llm = DefaultModel(temperature=0.0)
    summary = None

    if len(prompts) > 0:
        summary_prompt = PromptTemplate.from_template(summarizy_prompt_template)
        summary_chain = summary_prompt | llm
        summary_result = await summary_chain.ainvoke({ "text": "\n".join(prompts) })
        summary = summary_result.content

    if not isinstance(summary, str):
        summary = str(summary)

    return AireQuestionnaireResult(
        id=str(uuid.uuid4()),
        questionnaire_id=input.req.questionnaire_id, 
        timestamp=datetime.now(timezone.utc),
        answers=input.req.answers,
        summary=summary,
        prompts=prompts,
        user_id=input.auth.subject,
        privacy=input.req.privacy)


ProcessQuestionnaireChain = RunnableLambda(__process_questionnaire)
