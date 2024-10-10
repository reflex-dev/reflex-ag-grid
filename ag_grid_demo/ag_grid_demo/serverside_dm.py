import csv
import json
from pathlib import Path

from fastapi.requests import Request

import reflex as rx
import pandas as pd
from reflex_ag_grid import ag_grid, Datasource
from reflex_ag_grid.handlers import handle_filter_model

from .ag_grid_demo import app


wind_dataset = None
column_defs = [
    ag_grid.column_def(field="direction"),
    ag_grid.column_def(field="strength"),
    ag_grid.column_def(field="frequency"),
]


def get_wind_dataset_rows():
    global wind_dataset
    if wind_dataset is None:
        wind_dataset = pd.read_csv(
            "https://raw.githubusercontent.com/plotly/datasets/master/wind_dataset.csv"
        ).to_dict("records")
    return wind_dataset


class AgState(rx.State):
    _row_data: list[dict[str, str]]
    _last_sort_model: list[dict[str, str]] = []
    _last_filter_model: list[dict[str, str]] = []
    _last_search: str | None = None

    def _handle_search_query(self, row):
        if not self._last_search:
            return True
        if self._last_search in row["make"].lower():
            return True
        if self._last_search in row["model"].lower():
            return True
        return False

    def _handle_filter(self):
        if self._last_search or self._last_filter_model:
            self._row_data = [
                row
                for row in self._row_data
                if self._handle_search_query(row)
                and handle_filter_model(row, self._last_filter_model)
            ]

    def _handle_sort(self):
        # TODO: fix multi-column sorting
        for sort_col in self._last_sort_model:
            col_id = sort_col["colId"]
            sort = sort_col["sort"]
            self._row_data.sort(key=lambda x: x[col_id], reverse=sort == "desc")
    
    async def _apply_sort_model(self, sort_model):
        if sort_model == self._last_sort_model:
            # don't sort if the sort model hasn't changed
            return
        self._last_sort_model = sort_model
        await self.on_load()
    
    async def _apply_filter_model(self, filter_model):
        if filter_model == self._last_filter_model:
            # don't filter if the filter model hasn't changed
            return
        self._last_filter_model = filter_model
        await self.on_load()

    async def on_load(self):
        self._row_data = get_wind_dataset_rows()
        self._handle_filter()
        self._handle_sort()
        return my_grid.set_datasource(
            Datasource(uri=get_data_uri, rowCount=len(self._row_data)),
        )

    def handle_submit_search(self, form_data):
        search = form_data.get("search")
        if search is not None:
            search = search.lower()
        if search == self._last_search:
            # don't filter if the search hasn't changed
            return
        self._last_search = search
        return AgState.on_load


my_grid = ag_grid.root(
    id="my_grid",
    #rowData=AgState.row_data,
    column_defs=column_defs,
    default_col_def={"flex": 1},
    row_buffer=0,
    max_blocks_in_cache=2,
    cache_block_size=10,
    cache_overflow_size=2,
    max_concurrent_datasource_requests=2,
    infinite_initial_row_count=1,
    row_model_type="infinite",
    group_default_expanded=None,
)


@rx.page("/infinite", on_load=AgState.on_load)
def ag_grid_test_page() -> rx.Component:
    return rx.vstack(
        rx.form(
            rx.input(placeholder="Search...", id="search"),
            rx.button("Update"),
            on_submit=AgState.handle_submit_search,
        ),
        rx.box(
            my_grid,
            class_name=rx.color_mode_cond("ag-theme-quartz", "ag-theme-quartz-dark"),
            height="80vh",
            width="100%",
        ),
        width="100%",
    )


get_data_uri = (
    "/data?"
    "start=${params.startRow}"
    "&end=${params.endRow}"
    "&sort_model=${encodeURIComponent(JSON.stringify(params.sortModel))}"
    "&filter_model=${encodeURIComponent(JSON.stringify(params.filterModel))}"
)

@app.api.get("/data")
async def get_data(
    request: Request,
    start: int,
    end: int,
    filter_model: str = None,
    sort_model: str = None,
):
    try:
        token = request.headers["X-Reflex-Client-Token"]
    except KeyError:
        return []
    async with app.modify_state(rx.state._substate_key(token, rx.State)) as state:
        s_instance = await state.get_state(AgState)
        if filter_model is not None:
            try:
                await s_instance._apply_filter_model(json.loads(filter_model))
            except ValueError:
                pass
        if sort_model is not None:
            try:
                await s_instance._apply_sort_model(json.loads(sort_model))
            except ValueError:
                pass
        return tuple(s_instance._row_data[start:end])