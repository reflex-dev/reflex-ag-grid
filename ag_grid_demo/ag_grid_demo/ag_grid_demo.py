"""Welcome to Reflex! This file showcases the custom component in a basic app."""

from rxconfig import config

import reflex as rx

from reflex_ag_grid import ag_grid, ColumnDef, AGFilters

filename = f"{config.app_name}/{config.app_name}.py"


class State(rx.State):
    """The app state."""

    pass


columns = [
    ag_grid.column_def(
        header_name="Make",
        field="make",
        filter=ag_grid.filters.text,
        editable=True,
    ),
    ag_grid.column_def(
        header_name="Model",
        field="model",
        filter=ag_grid.filters.text,
    ),
    ag_grid.column_def(
        **{
            "header_name": "Price",
            "field": "price",
            "filter": ag_grid.filters.number,
        }  # type: ignore
    ),
]

data = [
    {"make": "Toyota", "model": "Celica", "price": 35000},
    {"make": "Ford", "model": "Mondeo", "price": 32000},
    {"make": "Porsche", "model": "Boxster", "price": 72000},
    {"make": "Toyota", "model": "Celica", "price": 35000},
    {"make": "Ford", "model": "Mondeo", "price": 32000},
    {"make": "Porsche", "model": "Boxster", "price": 72000},
]


def index():
    return rx.vstack(
        rx.box(
            ag_grid(
                id="grid_1",
                row_data=data,
                column_defs=columns,
                theme="balham",
            ),
            width="30vw",
            height="30vh",
        ),
        height="100vh",
        align="center",
    ), rx.color_mode.button(position="top-right")


# Add state and page to the app.
app = rx.App()
app.api.redoc_url = None
app.api.docs_url = None
app.add_page(index)
