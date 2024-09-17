"""Reflex custom component AgGrid."""

# For wrapping react guide, visit https://reflex.dev/docs/wrapping-react/overview/

from types import SimpleNamespace
import reflex as rx

import os
from typing import Any, Union
from .datasource import Datasource, SSRMDatasource
from reflex.components.props import PropsBase
from typing import Literal
from reflex.components.el import Div


def _on_ag_grid_event(event: rx.Var) -> list[rx.Var]:
    # Remove non-serializable keys from the event object
    return [
        rx.Var.create_safe(
            f"(() => {{let {{context, api, columnApi, column, node, event, eventPath, ...rest}} = {event}; return rest}})()",
            _var_is_string=False,
        )
    ]


def _on_selection_change_signature(event: rx.Var) -> list[rx.Var]:
    return [
        rx.Var.create_safe(f"{event}.api.getSelectedRows()", _var_is_string=False),
        rx.Var.create_safe(f"{event}.source", _var_is_string=False),
        rx.Var.create_safe(f"{event}.type", _var_is_string=False),
    ]


class AGFilters(SimpleNamespace):
    text = "agTextColumnFilter"
    number = "agNumberColumnFilter"
    date = "agDateColumnFilter"
    set = "agSetColumnFilter"
    multi = "agMultiColumnFilter"


class AGEditors(SimpleNamespace):
    text = "agTextCellEditor"
    large_text = "agLargeTextCellEditor"
    select = "agSelectCellEditor"
    rich_select = "agRichSelectCellEditor"
    number = "agNumberCellEditor"
    date = "agDateCellEditor"
    checkbox = "agCheckboxCellEditor"


class ColumnDef(PropsBase):
    field: str
    col_id: str | None = None
    type: str | None = None
    cell_data_type: bool | str | None = None
    hide: bool = False
    editable: bool | None = False
    filter: AGFilters | str | None = None
    floating_filter: bool = False
    header_name: str | None = None
    header_tooltip: str | None = None
    checkbox_selection: bool | None = False
    cell_editor: AGEditors | str | None = None
    cell_editor_params: dict[str, list[Any]] | None = None


class ColumnGroup(PropsBase):
    children: list["ColumnDef | ColumnGroup"]
    group_id: str
    marry_children: bool = False
    open_by_default: bool = False
    column_group_show: Literal["open", "closed"] = "open"
    header_name: str


class AgGrid(rx.Component):
    """Reflex AgGrid component is a high-performance and highly customizable component that wraps AG Grid, designed for creating rich datagrids."""

    # The library name for the ag-grid-react component
    library: str = "ag-grid-react@32.1.0"

    # The tag name for the AgGridReact component
    tag: str = "AgGridReact"

    # Variable for column definitions
    column_defs: rx.Var[list[dict[str, Any] | ColumnDef | ColumnGroup]]

    # Variable for row data
    row_data: rx.Var[list[dict[str, Any]]]

    # Variable for row selection type
    row_selection: rx.Var[str] = "single"

    # Variable to animate rows
    animate_rows: rx.Var[bool] = False

    # Variable for pagination
    pagination: rx.Var[bool] = False

    # Page size for pagination
    pagination_page_size: rx.Var[int] = 10

    # Selector for pagination page size options
    pagination_page_size_selector: rx.Var[list[int]] = [10, 25, 50]

    # Variable for the side bar configuration
    side_bar: rx.Var[Union[str, dict[str, Any], bool, list[str]]] = ""

    # Variable to indicate if tree data is used
    tree_data: rx.Var[bool] = rx.Var.create_safe(False)

    # Default column definition
    default_col_def: rx.Var[dict[str, Any]] = {}

    # Definition for the auto group column
    auto_group_column_def: rx.Var[Any] = {}

    # Data for pinned bottom rows
    pinned_bottom_row_data: rx.Var[list[dict[str, Any]]] = []

    # Default expanded group level
    group_default_expanded: rx.Var[int] | None = -1

    # Variable to indicate if group selects children
    group_selects_children: rx.Var[bool] = False

    # Variable to suppress row click selection
    suppress_row_click_selection: rx.Var[bool] = False

    # Event handler for getting the data path
    get_data_path: rx.EventHandler[lambda e0: [e0]]

    # Variable to allow unbalanced groups
    group_allow_unbalanced: rx.Var[bool] = False

    # Variable to show pivot panel
    pivot_panel_show: rx.Var[str] = "never"

    # Variable to show row group panel
    row_group_panel_show: rx.Var[str] = "never"

    # Variable to suppress aggregate function in header
    suppress_agg_func_in_header: rx.Var[bool] = False

    # Variable to lock group columns
    group_lock_group_columns: rx.Var[int] = 0

    # Variable to maintain column order
    maintain_column_order: rx.Var[bool] = False

    # Row model type for infinite/serverside row model
    row_model_type: rx.Var[str]

    # Cache block size for infinite/serverside row model
    cache_block_size: rx.Var[int]

    # Maximum blocks in cache for infinite/serverside row model
    max_blocks_in_cache: rx.Var[int]

    # Row buffer size for infinite/serverside row model
    row_buffer: rx.Var[int]

    # Cache overflow size for infinite/serverside row model
    cache_overflow_size: rx.Var[int]

    # Maximum concurrent datasource requests for infinite/serverside row model
    max_concurrent_datasource_requests: rx.Var[int]

    # Initial row count for infinite row model
    infinite_initial_row_count: rx.Var[int]

    # Datasource for infinite/serverside row model
    datasource: rx.Var[Datasource]

    # Event handler for getting the row ID
    get_row_id: rx.EventHandler[lambda e0: [e0]]

    # Event handler to check if it is a server-side group
    is_server_side_group: rx.EventHandler[lambda e0: [e0]]

    # Event handler to get the server-side group key
    get_server_side_group_key: rx.EventHandler[lambda e0: [e0]]

    # Server-side datasource for infinite/serverside row model
    server_side_datasource: rx.Var[SSRMDatasource]

    # Event handler to check if server-side group is open by default
    is_server_side_group_open_by_default: rx.EventHandler[lambda e0: [e0]]

    # Variable to enable client-side sort on server-side
    server_side_enable_client_side_sort: rx.Var[bool] = False

    # Event handler to get the child count
    get_child_count: rx.EventHandler[lambda e0: [e0]]

    # Event handler for cell click events
    on_cell_clicked: rx.EventHandler[_on_ag_grid_event]

    # Event handler for selection change events
    on_selection_changed: rx.EventHandler[_on_selection_change_signature]

    # Event handler for first data rendered events
    on_first_data_rendered: rx.EventHandler[_on_ag_grid_event]

    lib_dependencies: list[str] = [
        "ag-grid-community",
        "ag-grid-enterprise",
    ]

    # Change the aesthetic theme of the grid
    theme: rx.Var[Literal["quartz", "balham", "alpine", "material"]]

    @classmethod
    def create(
        cls,
        *children,
        id: str,
        data_path_key: str | None = None,
        is_server_side_group_key: str | None = None,
        get_server_side_group_key: str | None = None,
        server_side_group_open_level: int | None = None,
        child_count_key: str | None = None,
        row_id_key: str | None = None,
        **props,
    ) -> rx.Component:
        props.setdefault("id", id)

        # handle hierarchical data
        if data_path_key is not None:
            props["get_data_path"] = rx.Var.create_safe(
                f"(data) => data.{data_path_key}", _var_is_string=False
            ).to(rx.EventChain)

        if is_server_side_group_key is not None:
            props["is_server_side_group"] = rx.Var.create_safe(
                f"(data) => data.{is_server_side_group_key}", _var_is_string=False
            ).to(rx.EventChain)

        if get_server_side_group_key is not None:
            props["get_server_side_group_key"] = rx.Var.create_safe(
                f"(data) => data.{get_server_side_group_key}", _var_is_string=False
            ).to(rx.EventChain)

        if server_side_group_open_level is not None:
            props["server_side_group_open_level"] = rx.Var.create_safe(
                f"(params) => params.rowNode.level < {server_side_group_open_level}",
                _var_is_string=False,
            ).to(rx.EventChain)

        if child_count_key is not None:
            props["get_child_count"] = rx.Var.create_safe(
                f"(data) => data ? data.{child_count_key} : undefined",
                _var_is_string=False,
            ).to(rx.EventChain)

        if row_id_key is not None:
            props["get_row_id"] = rx.Var.create_safe(
                f"(params) => params.data.{row_id_key}", _var_is_string=False
            ).to(rx.EventChain)

        props["class_name"] = rx.match(
            props.get("theme", "quartz"),
            ("quartz", rx.color_mode_cond("ag-theme-quartz", "ag-theme-quartz-dark")),
            ("balham", rx.color_mode_cond("ag-theme-balham", "ag-theme-balham-dark")),
            ("alpine", rx.color_mode_cond("ag-theme-alpine", "ag-theme-alpine-dark")),
            (
                "material",
                rx.color_mode_cond("ag-theme-material", "ag-theme-material-dark"),
            ),
            "",
        )

        return super().create(*children, **props)

    def add_imports(self):
        return {
            "": [
                "ag-grid-community/styles/ag-grid.css",
                "ag-grid-community/styles/ag-theme-quartz.css",
                "ag-grid-community/styles/ag-theme-balham.css",
                "ag-grid-community/styles/ag-theme-material.css",
                "ag-grid-community/styles/ag-theme-alpine.css",
                "ag-grid-enterprise",
            ],
            "d3-format": ["format"],
            "ag-grid-enterprise": [
                "LicenseManager",
            ],
        }

    def add_custom_code(self) -> list[str]:
        ag_grid_license_key = os.getenv("AG_GRID_LICENSE_KEY")
        if ag_grid_license_key is not None:
            return [f"LicenseManager.setLicenseKey('{ag_grid_license_key}');"]
        return ["LicenseManager.setLicenseKey(null);"]

    def getSelectedRows(self, callback: rx.EventHandler) -> rx.event.EventSpec:
        return rx.call_script(
            f"refs['{self.get_ref()}']?.current?.api.getSelectedRows()",
            callback=callback,
        )

    def selectAll(self) -> rx.event.EventSpec:
        return rx.call_script(
            f"refs['{self.get_ref()}']?.current?.api.selectAll()",
        )

    def deselectAll(self) -> rx.event.EventSpec:
        return rx.call_script(
            f"refs['{self.get_ref()}']?.current?.api.deselectAll()",
        )

    def select_rows_by_key(self, keys: list[str]) -> rx.event.EventHandler:
        keys_var = rx.Var.create(keys, _var_is_string=False)
        script = f"""
let api = refs['{self.get_ref()}']?.current?.api
const selected_nodes = [];
let keys_set = new Set({keys_var});
api.forEachNode(function (node) {{
    if (keys_set.has(node.key)) {{
        selected_nodes.push(node);
    }} 
}});
api.deselectAll()
api.setNodesSelected({{ nodes: selected_nodes, newValue: true }});
"""
        return rx.call_script(script)  # type: ignore

    def log_nodes(self) -> rx.event.EventSpec:
        return rx.call_script(
            f"""
let api = refs['{self.get_ref()}']?.current?.api;
console.log("Logging nodes");
api.forEachNode(function (node) {{
    console.log(node.key);
}});
"""
        )

    def setGridOption(self, key: str, value: rx.Var) -> rx.event.EventSpec:
        return rx.call_script(
            f"refs['{self.get_ref()}']?.current?.api.setGridOption('{key}', {value})",
        )

    def set_datasource(self, datasource: Datasource):
        return self.setGridOption(
            key="datasource",
            value=rx.Var.create_safe(datasource, _var_is_string=False),
        )

    def set_serverside_datasource(self, datasource: SSRMDatasource):
        return self.setGridOption(
            key="serverSideDatasource",
            value=rx.Var.create_safe(datasource, _var_is_string=False),
        )

    def show_loading_overlay(self) -> rx.event.EventSpec:
        return rx.call_script(
            f"refs['{self.get_ref()}']?.current?.api.showLoadingOverlay()",
        )

    def show_no_rows_overlay(self) -> rx.event.EventSpec:
        return rx.call_script(
            f"refs['{self.get_ref()}']?.current?.api.showNoRowsOverlay()",
        )

    def hide_overlay(self) -> rx.event.EventSpec:
        return rx.call_script(
            f"refs['{self.get_ref()}']?.current?.api.hideOverlay()",
        )

    def redraw_rows(self) -> rx.event.EventSpec:
        return rx.call_script(
            f"refs['{self.get_ref()}']?.current?.api.redrawRows()",
        )


class WrappedAgGrid(AgGrid):
    """Reflex AgGrid component is a high-performance and highly customizable component that wraps AG Grid, designed for creating rich datagrids."""

    @classmethod
    def create(cls, *children, **props):
        width = props.pop("width", None)
        height = props.pop("height", None)
        return Div.create(
            super().create(*children, **props),
            width=width or "40vw",
            height=height or "25vh",
        )


class AgGridNamespace(rx.ComponentNamespace):
    column_def = ColumnDef
    column_group = ColumnGroup
    filters = AGFilters
    editors = AGEditors
    root = AgGrid.create
    __call__ = WrappedAgGrid.create


ag_grid = AgGridNamespace()
