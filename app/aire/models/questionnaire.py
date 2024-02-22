from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class AireQuestionnaireOptionType(str, Enum):
    """Questionnaire option types"""

    Range = "range"
    Checkbox = "checkbox"
    Open = "open"
    Number = "number"


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
    match: str | None
    multiline: bool = False


class AireQuestionnaireOptionNumber(AireQuestionnaireOption):
    """Questionnaire options for type 'number'"""

    min: int | None
    max: int | None
    default: int | None


class AireQuestionnaireQuestion(BaseModel):
    """Questionnaire question object"""

    id: str
    question: str
    keywords: list[str] | None
    prompt: str | None
    type: AireQuestionnaireOptionType
    options: AireQuestionnaireOption
    required: bool = False


class AireQuestionnaireSection(BaseModel):
    """Questionnaire section object"""

    id: str
    name: str
    keywords: list[str] | None
    questions: list[AireQuestionnaireQuestion]


class AireQuestionnairePreliminary(BaseModel):
    """Preliminary data extraction schema"""

    properties: dict
    required: list[str] | None


class AireQuestionnaire(BaseModel):
    """Questionnaire model"""

    id: str
    name: str
    lang: str
    modified: datetime | None
    keywords: list[str]
    preliminary: AireQuestionnairePreliminary | None
    content: list[AireQuestionnaireSection]


class AireQuestionnaireAnswer(BaseModel):
    """Questionnaire answer object"""

    question_id: str
    type: AireQuestionnaireOptionType
    question: str
    prompt: str | None
    answer: int | str | list[str] | dict | None
    options: dict | None


class AireQuestionnaireResult(BaseModel):
    """Processed Questionnaire results"""

    id: str | None
    questionnaire_id: str
    timestamp: datetime
    preliminary: dict | None
    answers: list[AireQuestionnaireAnswer]
    summary: str
    prompts: list[str] | None

class AireQuestionnaireProcessingRequest(BaseModel):
    """Request to process questionnaire results"""

    questionnaire_id: str
    answers: list[AireQuestionnaireAnswer]
