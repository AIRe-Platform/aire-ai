from pydantic import BaseModel

class CbrCategory(BaseModel):
    name: str
    keywords: list[str]

CBR_HEALTH = CbrCategory(
    name="Health",
    keywords=[
        "medical care",
        "rehabilitation"
        "nutrition",
        "hygiene",
        "mental health",
        "physical therapy",
        "occupational therapy",
        "speech therapy",
        "sensory impairments",
        "chronic conditions",
        "pain management",
        "mobility aids",
        "accessibility",
        "preventive care",
        "health education",
        "vaccinations",
        "medication adherence",
        "sexual health",
        "substance abuse",
        "health screening"
    ]
)

CBR_EDUCATION = CbrCategory(
    name="Education",
    keywords=[
        "literacy",
        "numeracy",
        "early childhood education",
        "primary education",
        "secondary education",
        "tertiary education",
        "vocational training",
        "special education",
        "inclusive education",
        "learning materials",
        "teacher training",
        "educational policy",
        "scholarships",
        "distance learning",
        "educational technology",
        "library access",
        "curriculum adaptation",
        "peer tutoring",
        "life skills",
        "educational assessment"
    ]
)

CBR_LIVELIHOOD = CbrCategory(
    name="Livelihood",
    keywords=[
        "employment",
        "income generation",
        "financial literacy",
        "entrepreneurship",
        "vocational skills",
        "microfinance",
        "job placement",
        "work accommodations",
        "agricultural development",
        "market access",
        "productivity tools",
        "business training",
        "savings groups",
        "economic policy",
        "cooperatives",
        "trade skills",
        "resource management",
        "networking",
        "social enterprise",
        "labor rights"
    ]
)

CBR_SOCIAL = CbrCategory(
    name="Social",
    keywords=[
        "family support",
        "peer support",
        "community inclusion",
        "social networks",
        "cultural activities",
        "sports and recreation",
        "accessible transportation",
        "social services",
        "housing",
        "legal rights",
        "advocacy",
        "stigma reduction",
        "networking events",
        "leisure activities",
        "friendship development",
        "conflict resolution",
        "civic participation",
        "community leadership",
        "social policy",
        "emergency response"
    ]
)

CBR_EMPOWERMENT = CbrCategory(
    name="Empowerment",
    keywords=[
        "self-advocacy",
        "decision-making",
        "rights awareness",
        "leadership training",
        "political participation",
        "legal aid",
        "representation",
        "accessibility standards",
        "gender equality",
        "youth empowerment",
        "disability awareness",
        "community organizing",
        "information access",
        "technology use",
        "financial independence",
        "mentorship",
        "networking",
        "skill development",
        "capacity building",
        "policy development"
    ]
)

CBR_KEYWORDS = (
    CBR_HEALTH.keywords + 
    CBR_EDUCATION.keywords +
    CBR_LIVELIHOOD.keywords + 
    CBR_SOCIAL.keywords + 
    CBR_EMPOWERMENT.keywords
)

CBR_CATEGORIES = [
    CBR_HEALTH.name + 
    CBR_EDUCATION.name +
    CBR_LIVELIHOOD.name + 
    CBR_SOCIAL.name + 
    CBR_EMPOWERMENT.name
]
