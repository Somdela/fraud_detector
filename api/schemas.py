from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Verdict(str, Enum):
    FRAUD          = "fraud"
    PROBABLE_FRAUD = "probable_fraud"   # uncertain + jamais communiqué
    UNCERTAIN      = "uncertain"
    LEGITIMATE     = "legitimate"


class FraudType(str, Enum):
    LOTTERY_SCAM   = "lottery_scam"
    ERROR_TRANSFER = "error_transfer"
    FAKE_OPERATOR  = "fake_operator"
    PIN_REQUEST    = "pin_request"
    FAKE_PROMOTION = "fake_promotion"
    UNKNOWN        = "unknown"
    NONE           = "none"


class SMSRequest(BaseModel):
    sms:       str           = Field(..., min_length=1, max_length=1600)
    sender:    Optional[str] = Field(None, description="Numéro de l'expéditeur (ex: +22670123456)")
    recipient: Optional[str] = Field(None, description="Numéro du destinataire — requis pour l'analyse comportementale")
    timestamp: Optional[datetime] = Field(None)

    model_config = {
        "json_schema_extra": {
            "example": {
                "sms": "Félicitations! Vous avez gagné 50000 FCFA. Appelez le +22670123456.",
                "sender": "+22670123456",
                "recipient": "+22671987654",
                "timestamp": "2026-07-04T10:30:00",
            }
        }
    }


class CommunicationInfo(BaseModel):
    known:      bool
    msg_count:  int
    first_seen: Optional[str] = None
    last_seen:  Optional[str] = None


class SMSResponse(BaseModel):
    verdict:              Verdict
    confidence:           float = Field(..., ge=0.0, le=1.0)
    fraud_type:           FraudType
    reason:               str
    communication_info:   Optional[CommunicationInfo] = None
    processing_time_ms:   float


class HealthResponse(BaseModel):
    status:       str
    model_loaded: bool
    version:      str
