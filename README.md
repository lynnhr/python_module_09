*This project was created as part of the 42 curriculum by lhaydar*

# Pydantic Models & Validation

Exercises: `ex0/space_station.py`, `ex1/alien_contact.py`, `ex2/space_crew.py`.
Run any of them directly, example: `python3 ex0/space_station.py`.

## Pydantic concepts used

- **`BaseModel`** : base class for a validated data model; fields are
  declared as type annotated class attributes.
- **`Field(...)`** : attaches constraints to a field (`min_length`,
  `max_length`, `ge`/`le` bounds, `default`, etc.) beyond its plain type.
- **`Enum` fields**: restrict a field to a fixed set of values
  (`ContactType`, `Rank`).
- **Nested models**: a field typed as another `BaseModel` (or a
  `list[...]` of one), e.g. `SpaceMission.crew: list[CrewMember]`; each
  item is validated independently.
- **`@model_validator(mode="after")`**: runs custom cross-field logic
  once all individual fields have already passed validation; must return
  `self`.
- **`ValidationError`**: raised by `model_validate()` on bad input;
  `.errors()` gives structured details (field path, message) for every
  failure at once.

## Using data_generator.tar

1. Extract it into a `tools/` directory:
   ```
   mkdir -p tools && tar -xf data_generator.tar -C tools
   ```
2. Generate the datasets (writes to `generated_data/` at the project root):
   ```
   python3 tools/data_exporter.py
   ```
   This produces `space_stations`, `alien_contacts`, and `space_missions` as
   `.json` / `.csv` / `.py`, plus `invalid_stations.json` and
   `invalid_contacts.json` for testing rejected data.

## Loading generated data in an exercise

```python
import json

with open("../generated_data/space_stations.json") as f:
    for data in json.load(f):
        station = SpaceStation.model_validate(data)
```
