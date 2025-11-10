from pymongo import MongoClient

from app.config import DB_NAME, MONGO_URI

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["UI.member_master"]


def get_member_by_name(name: str):
    return collection.find_one({"Name": {"$regex": name, "$options": "i"}})


def get_member_eligibility_by_name(name: str, year: str):
    member = get_member_by_name(name)
    if not member:
        return "Member not found"
    return member.get("eligible_year", {}).get(year, [])


def get_member_claims_by_name(name: str):
    member = get_member_by_name(name)
    if not member:
        return "Member not found"
    claims = member.get("Claims", [])
    return [
        {
            "claimId": c["claimId"],
            "totalChargeAmount": c["totalChargeAmount"],
            "status": c["claimStatus"],
        }
        for c in claims
    ]


def get_member_hccs_by_name(name: str):
    member = get_member_by_name(name)
    if not member:
        return "Member not found"
    return member.get("MOR", {}).get("DiseaseCoefficients", [])


def get_members_by_eligibility_year(year: str):
    year_str = str(year)
    members = collection.find(
        {"eligible_year."+year_str: {"$exists": True, "$ne": []}},  
        {"Name": 1, "DOB": 1, "MBI": 1, "deltaRiskScore": 1}
    ).limit(5)

    member_list = [
        {
            "Name": member.get("Name"),
            "DOB": member.get("DOB").isoformat() if member.get("DOB") else None,
            "MBI": member.get("MBI"),
            "deltaRiskScore": member.get("deltaRiskScore"),
        }
        for member in members
    ]

    if not member_list:
        return f"No members found for {year}"
    return member_list
