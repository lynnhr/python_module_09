from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class SpaceStation(BaseModel):
    station_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=1, max_length=50)
    crew_size: int = Field(ge=1, le=20)
    power_level: float = Field(ge=0.0, le=100.0)
    oxygen_level: float = Field(ge=0.0, le=100.0)
    last_maintenance: datetime
    is_operational: bool = True
    notes: str | None = Field(default=None, max_length=200)


def display_station(station: SpaceStation) -> None:
    status = "Operational" if station.is_operational else "Offline"
    print(f"ID: {station.station_id}")
    print(f"Name: {station.name}")
    print(f"Crew: {station.crew_size} people")
    print(f"Power: {station.power_level}%")
    print(f"Oxygen: {station.oxygen_level}%")
    print(f"Status: {status}")


def main() -> None:
    print("Space Station Data Validation")
    print("=" * 40)

    valid_data: dict[str, Any] = {
        "station_id": "ISS001",
        "name": "International Space Station",
        "crew_size": "6",
        "power_level": 85.5,
        "oxygen_level": 92.3,
        "last_maintenance": "2024-05-01T08:30:00",
        "notes": "Solar panel array replaced during the last EVA.",
    }

    try:
        station = SpaceStation.model_validate(valid_data)
        print("Valid station created:")
        display_station(station)
        print()
    except ValidationError as error:
        print(f"Unexpected error: {error}")

    print("=" * 40)
    print("Expected validation error:")

    invalid_data: dict[str, Any] = {
        "station_id": "BAD",
        "name": "Overcrowded Station",
        "crew_size": 25,
        "power_level": 50.0,
        "oxygen_level": 50.0,
        "last_maintenance": "2024-05-01T08:30:00",
    }

    try:
        SpaceStation.model_validate(invalid_data)
        print("No error raised: the model is too permissive!")
    except ValidationError as error:
        for detail in error.errors():
            print(detail["msg"])


if __name__ == "__main__":
    main()
