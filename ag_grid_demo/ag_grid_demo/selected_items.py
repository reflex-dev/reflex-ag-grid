import reflex as rx
from reflex_ag_grid import ag_grid
import pandas as pd

from .common import demo


df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/wind_dataset.csv"
)

column_defs = [
    ag_grid.column_def(field="direction"),
    ag_grid.column_def(field="strength"),
    ag_grid.column_def(field="frequency"),
]


class BasicGridState(rx.State):
    selection: list[dict[str, str]] = []


def selected_item(item: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.data_list.root(
            rx.foreach(
                item,
                lambda kv: rx.data_list.item(
                    rx.data_list.label(kv[0]),
                    rx.data_list.value(kv[1]),
                ),
            ),
        ),
    )


@demo(
    route="/selected-items",
    title="Selected Items",
    description="Handle grid selection events and display selected items in a separate panel.",
)
def selected_items_example():
    return rx.hstack(
        ag_grid(
            id="ag_grid_basic_1",
            row_data=df.to_dict("records"),
            column_defs=column_defs,
            row_selection="multiple",
            on_selection_changed=lambda rows, _0, _1: BasicGridState.set_selection(
                rows
            ),
            width="50%",
            height="71vh",
        ),
        rx.vstack(
            rx.heading(
                f"Selected Items ({BasicGridState.selection.length()})", size="4"
            ),
            rx.scroll_area(
                rx.hstack(
                    rx.foreach(
                        BasicGridState.selection,
                        selected_item,
                    ),
                    wrap="wrap",
                ),
            ),
            max_width="48%",
            height="71vh",
        ),
        width="100%",
    )
