from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ValidationError, model_validator


class ContactType(str, Enum):
    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: str | None = Field(default=None, max_length=500)
    is_verified: bool = False

    @model_validator(mode="after")
    def check_report_rules(self) -> "AlienContact":
        if not self.contact_id.startswith("AC"):
            raise ValueError('Contact ID must start with "AC"')

        if self.contact_type is ContactType.PHYSICAL:
            if not self.is_verified:
                raise ValueError("Physical contact reports must be verified")

        if self.contact_type is ContactType.TELEPATHIC:
            if self.witness_count < 3:
                raise ValueError(
                    "Telepathic contact requires at least 3 witnesses"
                )

        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError(
                "Strong signals (> 7.0) must include a received message"
            )

        return self


def display_contact(contact: AlienContact) -> None:
    print(f"ID: {contact.contact_id}")
    print(f"Type: {contact.contact_type.value}")
    print(f"Location: {contact.location}")
    print(f"Signal: {contact.signal_strength}/10")
    print(f"Duration: {contact.duration_minutes} minutes")
    print(f"Witnesses: {contact.witness_count}")
    if contact.message_received is not None:
        print(f"Message: '{contact.message_received}'")
    print(f"Verified: {contact.is_verified}")


def show_errors(error: ValidationError) -> None:
    for detail in error.errors():
        field = ".".join(str(part) for part in detail["loc"])
        message = detail["msg"].removeprefix("Value error, ")
        print(f"{field}: {message}" if field else message)


def try_bad_report(title: str, data: dict[str, Any]) -> None:
    print("=" * 38)
    print(f"Expected validation error ({title}):")
    try:
        AlienContact.model_validate(data)
        print("No error raised: the model is too permissive!")
    except ValidationError as error:
        show_errors(error)


def main() -> None:
    print("Alien Contact Log Validation")
    print("=" * 38)

    valid_data: dict[str, Any] = {
        "contact_id": "AC_2024_001",
        "timestamp": "2024-07-14T22:15:00",
        "location": "Area 51, Nevada",
        "contact_type": "radio",
        "signal_strength": 8.5,
        "duration_minutes": 45,
        "witness_count": 5,
        "message_received": "Greetings from Zeta Reticuli",
    }

    try:
        contact = AlienContact.model_validate(valid_data)
        print("Valid contact report:")
        display_contact(contact)
    except ValidationError as error:
        print("Unexpected rejection:")
        show_errors(error)

    try_bad_report("ID does not start with AC", {
        "contact_id": "XX_2024_002",
        "timestamp": "2024-07-15T09:00:00",
        "location": "Tunguska, Siberia",
        "contact_type": "visual",
        "signal_strength": 3.0,
        "duration_minutes": 15,
        "witness_count": 2,
    })

    try_bad_report("Unverified physical contact", {
        "contact_id": "AC_2024_003",
        "timestamp": "2024-07-16T01:30:00",
        "location": "Rendlesham Forest",
        "contact_type": "physical",
        "signal_strength": 5.0,
        "duration_minutes": 20,
        "witness_count": 4,
    })

    try_bad_report("Telepathic contact with 2 witnesses", {
        "contact_id": "AC_2024_004",
        "timestamp": "2024-07-17T03:00:00",
        "location": "Roswell, New Mexico",
        "contact_type": "telepathic",
        "signal_strength": 2.0,
        "duration_minutes": 10,
        "witness_count": 2,
    })

    try_bad_report("Strong signal with no message", {
        "contact_id": "AC_2024_005",
        "timestamp": "2024-07-18T18:45:00",
        "location": "Atacama Desert",
        "contact_type": "radio",
        "signal_strength": 9.2,
        "duration_minutes": 60,
        "witness_count": 3,
    })

    try_bad_report("Signal outside the 0-10 scale", {
        "contact_id": "AC_2024_006",
        "timestamp": "2024-07-19T12:00:00",
        "location": "Nazca Lines",
        "contact_type": "visual",
        "signal_strength": 42.0,
        "duration_minutes": 5,
        "witness_count": 1,
    })


if __name__ == "__main__":
    main()
