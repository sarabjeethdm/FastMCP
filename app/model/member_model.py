from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class ClaimModel(BaseModel):
    claimId: str
    totalChargeAmount: str
    claimStatus: str
    cptCode: List[str]
    diagnosis: List[str]
    hcc_map: Dict[str, str]

class MemberModel(BaseModel):
    MBI: str
    Name: str
    DOB: datetime
    Claims: List[ClaimModel]
    MOR: Optional[dict] = {}
    eligible_year: Dict[str, List[int]] = {}

