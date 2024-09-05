"""Welcome to Reflex! This file showcases the custom component in a basic app."""

from rxconfig import config

import reflex as rx

from reflex_ag_grid import ag_grid

filename = f"{config.app_name}/{config.app_name}.py"


class State(rx.State):
    """The app state."""

    pass


columns = [
    {"filter": "agTextColumnFilter", "field": "make"},
    {"filter": "agTextColumnFilter", "field": "model"},
    {"filter": "agNumberColumnFilter", "field": "price"},
]

data = [
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
            ),
            width="50vw",
            height="50vh",
        ),
        height="100vh",
        align="center",
    ), rx.color_mode.button(position="top-right")


# Add state and page to the app.
app = rx.App()
app.api.redoc_url = None
app.api.docs_url = None
app.add_page(index)
