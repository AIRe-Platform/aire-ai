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
        "Literacy",
        "Numeracy",
        "Early childhood education",
        "Primary education",
        "Secondary education",
        "Tertiary education",
        "Vocational training",
        "Special education",
        "Inclusive education",
        "Learning materials",
        "Teacher training",
        "Educational policy",
        "Scholarships",
        "Distance learning",
        "Educational technology",
        "Library access",
        "Curriculum adaptation",
        "Peer tutoring",
        "Life skills",
        "Educational assessment"
    ]
)

CBR_LIVELIHOOD = CbrCategory(
    name="Livelihood",
    keywords=[
        "Employment",
        "Income generation",
        "Financial literacy",
        "Entrepreneurship",
        "Vocational skills",
        "Microfinance",
        "Job placement",
        "Work accommodations",
        "Agricultural development",
        "Market access",
        "Productivity tools",
        "Business training",
        "Savings groups",
        "Economic policy",
        "Cooperatives",
        "Trade skills",
        "Resource management",
        "Networking",
        "Social enterprise",
        "Labor rights"
    ]
)

CBR_SOCIAL = CbrCategory(
    name="Social",
    keywords=[
        "Family support",
        "Peer support",
        "Community inclusion",
        "Social networks",
        "Cultural activities",
        "Sports and recreation",
        "Accessible transportation",
        "Social services",
        "Housing",
        "Legal rights",
        "Advocacy",
        "Stigma reduction",
        "Networking events",
        "Leisure activities",
        "Friendship development",
        "Conflict resolution",
        "Civic participation",
        "Community leadership",
        "Social policy",
        "Emergency response"
    ]
)

CBR_EMPOWERMENT = CbrCategory(
    name="Empowerment",
    keywords=[
        "Self-advocacy",
        "Decision-making",
        "Rights awareness",
        "Leadership training",
        "Political participation",
        "Legal aid",
        "Representation",
        "Accessibility standards",
        "Gender equality",
        "Youth empowerment",
        "Disability awareness",
        "Community organizing",
        "Information access",
        "Technology use",
        "Financial independence",
        "Mentorship",
        "Networking",
        "Skill development",
        "Capacity building",
        "Policy development"
    ]
)

CBR_KEYWORDS = (
    CBR_HEALTH.keywords + 
    CBR_EDUCATION.keywords +
    CBR_LIVELIHOOD.keywords + 
    CBR_SOCIAL.keywords + 
    CBR_EMPOWERMENT.keywords
)
