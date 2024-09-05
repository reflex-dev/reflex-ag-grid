"""Handlers for the reflex_ag_grid component."""


def handle_text_filter(value, filter_def) -> bool:
    type = filter_def.get("type", "contains")
    filter = filter_def.get("filter", "").lower()
    if type == "contains":
        return filter in value
    if type == "notContains":
        return filter not in value
    if type == "equals":
        return value == filter
    if type == "notEqual":
        return value != filter
    if type == "startsWith":
        return value.startswith(filter)
    if type == "endsWith":
        return value.endswith(filter)
    if type == "blank":
        return not value
    if type == "notBlank":
        return bool(value)
    assert False, f"type {type} does not exist"


def handle_number_filter(value, filter_def) -> bool:
    type = filter_def.get("type", "equals")
    filter = filter_def.get("filter")
    if type == "equals":
        return value == filter
    if type == "notEqual":
        return value != filter
    if type == "greaterThan":
        return value > filter
    if type == "greaterThanOrEqual":
        return value >= filter
    if type == "lessThan":
        return value < filter
    if type == "lessThanOrEqual":
        return value <= filter
    if type == "inRange":
        return filter <= value <= filter_def.get("filterTo")
    if type == "blank":
        return not value
    if type == "notBlank":
        return bool(value)

    assert False, f"type {type} does not exist"


def handle_filter_def(value, filter_def) -> bool:
    if not filter_def:
        return True
    operator = filter_def.get("operator", "").lower()
    if operator == "and":
        return all(
            handle_filter_def(value, sub_filter)
            for sub_filter in filter_def.get("conditions", [])
        )
    elif operator == "or":
        return any(
            handle_filter_def(value, sub_filter)
            for sub_filter in filter_def.get("conditions", [])
        )
    filter_type = filter_def.get("filterType", "text")
    if filter_type == "text":
        return handle_text_filter(value.lower(), filter_def)
    if filter_type == "number":
        return handle_number_filter(value, filter_def)
    return False


def handle_filter_model(row, filter_model) -> bool:
    if not filter_model:
        return True
    for field, filter_def in filter_model.items():
        try:
            if not handle_filter_def(row[field], filter_def):
                return False
        except Exception as e:
            print(f"Error filtering {field} of {row}: {e}")
            return False
    return True
