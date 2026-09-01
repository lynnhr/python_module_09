from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def check_mission_rules(self) -> "SpaceMission":
        if not self.mission_id.startswith("M"):
            raise ValueError('Mission ID must start with "M"')

        leaders = [
            member
            for member in self.crew
            if member.rank in (Rank.COMMANDER, Rank.CAPTAIN)
        ]
        if not leaders:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        if self.duration_days > 365:
            experienced = [
                member for member in self.crew
                if member.years_experience >= 5
            ]
            if len(experienced) * 2 < len(self.crew):
                raise ValueError(
                    "Long missions need at least 50% experienced crew "
                    "(5+ years)"
                )

        inactive = [
            member.name for member in self.crew if not member.is_active
        ]
        if inactive:
            raise ValueError(
                f"All crew members must be active: {', '.join(inactive)}"
            )

        return self


def display_mission(mission: SpaceMission) -> None:
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Launch date: {mission.launch_date}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Status: {mission.mission_status}")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for member in mission.crew:
        print(f"- {member.name} ({member.rank.value})"
              f" - {member.specialization}")


def show_errors(error: ValidationError) -> None:
    for detail in error.errors():
        field = ".".join(str(part) for part in detail["loc"])
        message = detail["msg"].removeprefix("Value error, ")
        print(f"{field}: {message}" if field else message)


COMMANDER: dict[str, Any] = {
    "member_id": "CM001",
    "name": "Sarah Connor",
    "rank": "commander",
    "age": 45,
    "specialization": "Mission Command",
    "years_experience": 20,
}
LIEUTENANT: dict[str, Any] = {
    "member_id": "LT002",
    "name": "John Smith",
    "rank": "lieutenant",
    "age": 34,
    "specialization": "Navigation",
    "years_experience": 8,
}
OFFICER: dict[str, Any] = {
    "member_id": "OF003",
    "name": "Alice Johnson",
    "rank": "officer",
    "age": 29,
    "specialization": "Engineering",
    "years_experience": 3,
}
CADET: dict[str, Any] = {
    "member_id": "CD004",
    "name": "Bob Miller",
    "rank": "cadet",
    "age": 22,
    "specialization": "Life Support",
    "years_experience": 1,
}
INACTIVE_CAPTAIN: dict[str, Any] = {
    "member_id": "CP005",
    "name": "Ellen Ripley",
    "rank": "captain",
    "age": 41,
    "specialization": "Xenobiology",
    "years_experience": 15,
    "is_active": False,
}


def make_mission(**changes: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "mission_id": "M2024_MARS",
        "mission_name": "Mars Colony Establishment",
        "destination": "Mars",
        "launch_date": "2024-11-01T06:00:00",
        "duration_days": 900,
        "crew": [COMMANDER, LIEUTENANT, OFFICER],
        "budget_millions": 2500.0,
    }
    data.update(changes)
    return data


def try_bad_mission(title: str, data: dict[str, Any]) -> None:
    print("=" * 41)
    print(f"Expected validation error ({title}):")
    try:
        SpaceMission.model_validate(data)
        print("No error raised: the model is too permissive!")
    except ValidationError as error:
        show_errors(error)


def main() -> None:
    print("Space Mission Crew Validation")
    print("=" * 41)

    lead = CrewMember.model_validate(COMMANDER)
    print(f"Standalone crew member: {lead.name} ({lead.rank.value}),"
          f" {lead.years_experience} years")
    print("=" * 41)

    try:
        mission = SpaceMission.model_validate(make_mission())
        print("Valid mission created:")
        display_mission(mission)
    except ValidationError as error:
        print("Unexpected rejection:")
        show_errors(error)

    try_bad_mission(
        "ID does not start with M",
        make_mission(mission_id="X2024_MARS"),
    )

    try_bad_mission(
        "No Commander or Captain",
        make_mission(crew=[OFFICER, CADET]),
    )

    try_bad_mission(
        "Long mission with an inexperienced crew",
        make_mission(crew=[COMMANDER, OFFICER, CADET]),
    )

    try_bad_mission(
        "Inactive crew member",
        make_mission(crew=[COMMANDER, INACTIVE_CAPTAIN]),
    )

    try_bad_mission(
        "Mission over budget",
        make_mission(budget_millions=99999.0),
    )

    child = dict(CADET, age=12)
    try_bad_mission(
        "Crew member too young (nested error)",
        make_mission(crew=[COMMANDER, child]),
    )


if __name__ == "__main__":
    main()
