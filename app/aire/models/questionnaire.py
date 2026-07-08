# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional, Any


class AireQuestionnaireOptionType(str, Enum):
    """Questionnaire option types"""
    Range = "range"
    Checkbox = "checkbox"
    Open = "open"
    Number = "number"
    Content = "content"


class AireQuestionnaireOption(BaseModel):
    """Questionnaire option base class"""
    pass


class AireQuestionnaireOptionRange(AireQuestionnaireOption):
    """Questionnaire options for type 'range'"""
    min: int
    max: int


class AireQuestionnaireOptionCheckbox(AireQuestionnaireOption):
    """Questionnaire options for type 'checkbox'"""
    values: list[str]
    multiselect: bool = True


class AireQuestionnaireOptionOpen(AireQuestionnaireOption):
    """Questionnaire options for type 'open'"""
    max_len: int
    match: Optional[str] = None
    multiline: bool = False


class AireQuestionnaireOptionNumber(AireQuestionnaireOption):
    """Questionnaire options for type 'number'"""
    min: Optional[int] = None
    max: Optional[int] = None
    default: Optional[int] = None


class AireQuestionnaireQuestion(BaseModel):
    """Questionnaire question object"""
    id: str
    question: str
    keywords: Optional[list[str]] = None
    prompt: Optional[str] = None
    type: AireQuestionnaireOptionType
    options: AireQuestionnaireOption
    required: bool = False


class AireQuestionnaireSection(BaseModel):
    """Questionnaire section object"""
    id: str
    name: str
    keywords: Optional[list[str]] = None
    questions: list[AireQuestionnaireQuestion]


class AireQuestionnaire(BaseModel):
    """Questionnaire model"""
    id: str
    name: str
    lang: str
    modified: Optional[datetime] = None
    keywords: list[str]
    content: Optional[list[AireQuestionnaireSection]]
    external_url: Optional[str]


class AireQuestionnaireAnswer(BaseModel):
    """Questionnaire answer object"""
    questionnaire_id: str
    question_id: str
    type: AireQuestionnaireOptionType
    question: str
    prompt: Optional[str] = None
    answer: Optional[int | str | list[str] | dict] = None
    options: Optional[dict[str, Any]] = None


class AireQuestionnaireResult(BaseModel):
    """Processed Questionnaire results"""
    id: Optional[str] = None
    questionnaire_id: str
    timestamp: datetime
    answers: list[AireQuestionnaireAnswer]
    summary: str
    prompts: Optional[list[str]] = None


class AireQuestionnaireProcessingRequest(BaseModel):
    """Request to process questionnaire results"""
    questionnaire_id: str
    answers: list[AireQuestionnaireAnswer]


class AireQuestionnaireMetadata(BaseModel):
    """Questionnaire embedding metadata"""
    id: str
    language: Optional[str] = None
    relevance: Optional[float] = None

    