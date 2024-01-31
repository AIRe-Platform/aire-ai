from pydantic import BaseModel, ConfigDict, Extra
from enum import Enum
from datetime import datetime

class AireSurveyOptionType(str, Enum):
    """Survey option types"""

    Range = "range"
    Checkbox = "checkbox"
    Open = "open"
    Number = "number"


class AireSurveyOption(BaseModel):
    """Survey option base class"""

    type: AireSurveyOptionType
    required: bool = False


class AireSurveyOptionRange(AireSurveyOption):
    """Survey options for type 'range'"""

    min: int
    max: int


class AireSurveyOptionCheckbox(AireSurveyOption):
    """Survey options for type 'checkbox'"""

    values: list[str]
    multiselect: bool = True


class AireSurveyOptionOpen(AireSurveyOption):
    """Survey options for type 'open'"""

    max_len: int
    match: str | None
    multiline: bool = False


class AireSurveyOptionNumber(AireSurveyOption):
    """Survey options for type 'number'"""

    min: int | None
    max: int | None
    default: int | None


class AireSurveyQuestion(BaseModel):
    """Survey question object"""

    id: str
    question: str
    keywords: list[str] | None
    prompt: str | None
    options: AireSurveyOption
    required: bool = False


class AireSurveySection(BaseModel):
    """Survey section object"""

    id: str
    name: str
    keywords: list[str] | None
    questions: list[AireSurveyQuestion]


class AireSurveyPreliminary(BaseModel):
    """Preliminary data extraction schema"""

    properties: dict
    required: list[str] | None


class AireSurvey(BaseModel):
    """Survey model"""

    id: str
    name: str
    lang: str
    modified: datetime
    keywords: list[str]
    preliminary: AireSurveyPreliminary
    content: list[AireSurveySection]


class AireSurveyAnswer(BaseModel):
    """Survey answer object"""

    question_id: str
    type: AireSurveyOptionType
    question: str
    prompt: str | None
    answer: int | str | None

    model_config = ConfigDict(extra=Extra.allow)


class AireSurveyResult(BaseModel):
    """Processed survey results"""

    id: str | None
    survey_id: str
    timestamp: datetime
    preliminary: dict | None
    answers: list[AireSurveyAnswer]
    summary: str
    prompts: list[str]
