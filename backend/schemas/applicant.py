"""
applicant.py
Pydantic schemas for all ScoreSeva API request and response models.
Used by all routers for input validation and response serialization.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────────
class GenderEnum(str, Enum):
    M = "M"
    F = "F"

class EducationEnum(str, Enum):
    higher         = "Higher education"
    secondary      = "Secondary / secondary special"
    incomplete     = "Incomplete higher"
    lower_secondary = "Lower secondary"
    academic       = "Academic degree"

class IncomeSourceEnum(str, Enum):
    working     = "Working"
    commercial  = "Commercial associate"
    pensioner   = "Pensioner"
    state       = "State servant"
    unemployed  = "Unemployed"
    student     = "Student"
    maternity   = "Maternity leave"
    businessman = "Businessman"

class FamilyStatusEnum(str, Enum):
    married          = "Married"
    single           = "Single / not married"
    civil_marriage   = "Civil marriage"
    separated        = "Separated"
    widow            = "Widow"


# ── Request Schema ────────────────────────────────────────────────────
class ApplicantInput(BaseModel):
    """
    Full applicant profile for credit scoring.
    All fields map directly to the XGBoost feature set from Phase 1B.
    """

    # Financial
    annual_income: float = Field(
        ..., ge=0, le=10_000_000,
        description="Annual income in INR",
        example=180000
    )
    loan_amount: float = Field(
        ..., ge=1000, le=10_000_000,
        description="Requested loan amount in INR",
        example=50000
    )
    monthly_emi: float = Field(
        ..., ge=100, le=500_000,
        description="Expected monthly EMI in INR",
        example=2500
    )

    # Personal
    age_years: int = Field(
        ..., ge=18, le=80,
        description="Applicant age in years",
        example=38
    )
    gender: GenderEnum = Field(
        ..., example="M"
    )
    num_children: int = Field(
        default=0, ge=0, le=20,
        description="Number of dependent children",
        example=2
    )
    family_size: int = Field(
        default=2, ge=1, le=20,
        description="Total family members",
        example=4
    )

    # Employment
    employment_years: float = Field(
        ..., ge=0, le=50,
        description="Years at current employment (0 if unemployed)",
        example=8.0
    )
    income_source: IncomeSourceEnum = Field(
        default=IncomeSourceEnum.working,
        example="Working"
    )
    occupation: Optional[str] = Field(
        default="Unknown",
        example="Drivers"
    )

    # Credit history
    ext_credit_score_1: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="External credit signal 1 (0-1)",
        example=0.55
    )
    ext_credit_score_2: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="External credit signal 2 (0-1)",
        example=0.62
    )
    ext_credit_score_3: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="External credit signal 3 (0-1)",
        example=0.58
    )
    credit_enquiries_last_year: int = Field(
        default=0, ge=0, le=50,
        description="Number of credit bureau enquiries in last 12 months",
        example=0
    )

    # Assets
    owns_car: bool = Field(default=False, example=False)
    owns_property: bool = Field(default=False, example=False)

    # Identity stability
    id_stability_years: float = Field(
        default=2.0, ge=0.0, le=30.0,
        description="Years since ID document was last updated",
        example=3.2
    )

    # Region
    region_risk_rating: int = Field(
        default=2, ge=1, le=3,
        description="1=Urban, 2=Semi-urban, 3=Rural",
        example=2
    )

    # Education and family
    education_level: EducationEnum = Field(
        default=EducationEnum.secondary,
        example="Secondary / secondary special"
    )
    family_status: FamilyStatusEnum = Field(
        default=FamilyStatusEnum.married,
        example="Married"
    )

    # India-specific digital signals
    upi_consistency_score: float = Field(
        default=50.0, ge=0.0, le=100.0,
        description="UPI transaction consistency score (0-100)",
        example=81.0
    )
    phone_bill_regularity: float = Field(
        default=50.0, ge=0.0, le=100.0,
        description="Phone bill payment regularity (0-100)",
        example=88.0
    )
    geo_stability_score: float = Field(
        default=50.0, ge=0.0, le=100.0,
        description="Geographic location stability (0-100)",
        example=76.0
    )
    ecommerce_payment_score: float = Field(
        default=50.0, ge=0.0, le=100.0,
        description="E-commerce payment behavior score (0-100)",
        example=60.0
    )
    social_network_risk: float = Field(
        default=0.2, ge=0.0, le=1.0,
        description="Social network credit risk (0=safe, 1=risky)",
        example=0.12
    )
    app_usage_score: float = Field(
        default=50.0, ge=0.0, le=100.0,
        description="App usage consistency score (0-100)",
        example=74.0
    )

    @field_validator('family_size')
    @classmethod
    def family_size_gte_children(cls, v, info):
        if 'num_children' in info.data and v < info.data['num_children']:
            raise ValueError(
                'family_size must be >= num_children'
            )
        return v

    @field_validator('monthly_emi')
    @classmethod
    def emi_below_income(cls, v, info):
        if 'annual_income' in info.data:
            monthly_income = info.data['annual_income'] / 12
            if v > monthly_income * 0.9:
                raise ValueError(
                    'monthly_emi cannot exceed 90% of monthly income'
                )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "annual_income": 180000,
                "loan_amount": 50000,
                "monthly_emi": 2500,
                "age_years": 38,
                "gender": "M",
                "employment_years": 8.0,
                "upi_consistency_score": 81.0,
                "phone_bill_regularity": 88.0,
                "geo_stability_score": 76.0,
                "ecommerce_payment_score": 60.0,
                "social_network_risk": 0.12,
                "app_usage_score": 74.0,
                "ext_credit_score_1": 0.55,
                "ext_credit_score_2": 0.62,
                "ext_credit_score_3": 0.58,
            }
        }


# ── Response Schemas ──────────────────────────────────────────────────
class RiskBand(BaseModel):
    band: str
    color: str
    label: str
    recommendation: str
    suggested_rate: str


class ScoreResponse(BaseModel):
    applicant_id:         Optional[str] = None
    scoreseva_score:      int
    default_probability:  float
    risk_band:            RiskBand
    top_positive_factors: list[str]
    top_negative_factors: list[str]
    model_version:        str = "1.0.0"


class FraudResponse(BaseModel):
    fraud_score:          float
    isolation_risk:       float
    rule_penalty:         float
    red_flags:            list[str]
    red_flag_count:       int
    verdict:              str
    action:               str
    color:                str


class TrajectoryPoint(BaseModel):
    natural:  int
    improved: int


class Recommendation(BaseModel):
    action:       str
    current:      str
    target:       str
    score_impact: str
    timeframe:    str


class TrajectoryResponse(BaseModel):
    current_score:         int
    trajectory:            dict[str, TrajectoryPoint]
    recommendations:       list[Recommendation]
    total_potential_gain:  int


class NLPResponse(BaseModel):
    nlp_credit_score:   float
    sentiment_score:    float
    risk_probability:   float
    risk_label:         str
    key_signals:        dict[str, float]


class HealthResponse(BaseModel):
    status:      str
    app_name:    str
    version:     str
    environment: str
    models:      dict[str, bool]


class NLPRequest(BaseModel):
    """
    Free-text input for NLP psychometric analysis.
    Accepts up to 3 applicant responses to standard questions.
    """
    why_loan: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Why do you need this loan?",
        example=(
            "I need this loan to buy a sewing machine and grow "
            "my tailoring business. I save 25 percent of my "
            "income every month and will repay within 18 months."
        )
    )
    repayment_plan: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=1000,
        description="How do you plan to repay this loan?",
        example=(
            "I earn 15000 per month from my shop and the EMI "
            "will be only 2000 so repayment is very manageable."
        )
    )
    financial_situation: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=1000,
        description="Describe your financial situation in one sentence.",
        example=(
            "My finances are stable with regular income and "
            "I have never missed a payment in my life."
        )
    )
    applicant_id: Optional[str] = Field(
        default=None,
        description="Optional applicant ID for tracking",
        example="APP-2024-001"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "why_loan": (
                    "I need this loan to buy equipment for my "
                    "small tailoring business which will increase "
                    "my monthly income by at least 30 percent."
                ),
                "repayment_plan": (
                    "I plan to repay in 12 equal monthly "
                    "installments from my auto-rickshaw earnings "
                    "which are stable and consistent."
                ),
                "financial_situation": (
                    "My finances are stable with regular income "
                    "from my shop and I have never missed any "
                    "payment in my life."
                )
            }
        }


class NLPDetailedResponse(BaseModel):
    """
    Full NLP psychometric analysis response.
    """
    applicant_id:         Optional[str]   = None
    combined_text:        str
    nlp_credit_score:     float
    sentiment_score:      float
    risk_probability:     float
    risk_label:           str
    psychometric_signals: dict
    text_insights:        list[str]
    model_version:        str = "1.0.0"
