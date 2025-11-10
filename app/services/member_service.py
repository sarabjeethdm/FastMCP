from pymongo import MongoClient

from app.config import DB_NAME, MONGO_URI

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["UI.member_master"]


def get_member_by_name(
    name: str, health_plan_id: str = None, year_of_service: int = None
):
    """
    Return single member filtered by name, optional healthPlanId and yearOfService
    """
    query = {"Name": {"$regex": name, "$options": "i"}}
    if health_plan_id:
        query["healthPlanId"] = health_plan_id
    if year_of_service:
        query["yearOfService"] = year_of_service

    return collection.find_one(query)


def get_member_eligibility_by_name(
    name: str, year: str, health_plan_id: str = None, year_of_service: int = None
):
    member = get_member_by_name(name, health_plan_id, year_of_service)
    if not member:
        return "Member not found"
    return member.get("eligible_year", {}).get(year, [])


def get_member_claims_by_name(
    name: str, health_plan_id: str = None, year_of_service: int = None
):
    member = get_member_by_name(name, health_plan_id, year_of_service)
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


def get_member_hccs_by_name(
    name: str, health_plan_id: str = None, year_of_service: int = None
):
    member = get_member_by_name(name, health_plan_id, year_of_service)
    if not member:
        return "Member not found"
    return member.get("MOR", {}).get("DiseaseCoefficients", [])


def get_members_by_eligibility_year(
    year: str, health_plan_id: str = None, year_of_service: int = None
):
    query = {"eligible_year." + str(year): {"$exists": True, "$ne": []}}
    if health_plan_id:
        query["healthPlanId"] = health_plan_id
    if year_of_service:
        query["yearOfService"] = year_of_service

    members = collection.find(
        query,
        {"Name": 1, "DOB": 1, "MBI": 1, "deltaRiskScore": 1},
    ).limit(
        50
    )  # you can adjust limit

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


def get_all_members(
    limit: int = 50, health_plan_id: str = None, year_of_service: int = None
):
    query = {}
    if health_plan_id:
        query["healthPlanId"] = health_plan_id
    if year_of_service:
        query["yearOfService"] = year_of_service

    print(f"query : {query}")

    members = collection.find(
        query,
        {
            "Name": 1,
            "DOB": 1,
            "MBI": 1,
            "deltaRiskScore": 1,
            "yearOfService": 1,
            "healthPlanId": 1,
        },
    ).limit(limit)

    member_list = [
        {
            "Name": m.get("Name"),
            "DOB": m.get("DOB").isoformat() if m.get("DOB") else None,
            "MBI": m.get("MBI"),
            "deltaRiskScore": m.get("deltaRiskScore"),
            "healthPlanId": m.get("healthPlanId"),
            "yearOfService": m.get("yearOfService"),
        }
        for m in members
    ]
    return member_list


def get_members_by_delta_riskscore(
    operator: str, value: float, health_plan_id: str = None, year_of_service: int = None
):
    operator_map = {
        "lt": "$lt",
        "lte": "$lte",
        "eq": "$eq",
        "gte": "$gte",
        "gt": "$gt",
    }

    mongo_operator = operator_map.get(operator)
    if not mongo_operator:
        return {"error": "Invalid operator"}

    query = {"deltaRiskScore": {mongo_operator: value}}
    if health_plan_id:
        query["healthPlanId"] = health_plan_id
    if year_of_service:
        query["yearOfService"] = year_of_service

    members = list(
        collection.find(
            query, {"_id": 0, "MBI": 1, "Name": 1, "deltaRiskScore": 1}
        ).limit(5)
    )
    return members
