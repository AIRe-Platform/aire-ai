# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from server import app
from errors import *
from utils.auth import *

from aire.models.questionnaire import *
from bot.chains.questionnaire import ProcessQuestionnaireChain, QuestionnaireChainInput

from typing import Annotated
from fastapi import Depends, Body

@app.post("/questionnaire-results",
          description="Process questionnaire results",
          tags=["Questionnaires"])
async def process_questionnaire(
    auth: Annotated[AireAuth | None, Depends(verify_token)],
    request: Annotated[AireQuestionnaireProcessingRequest, Body()]
) -> AireQuestionnaireResult:
    
    if auth == None:
        raise UNAUTH_EXCEPTION
    if not AireScope.QuestionnaireRead in auth.scopes:
        raise FORBIDDEN_EXCEPTION
        
    input = QuestionnaireChainInput(req=request, auth=auth)
    return ProcessQuestionnaireChain.invoke(input)
