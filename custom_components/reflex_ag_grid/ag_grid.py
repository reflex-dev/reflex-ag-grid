"""Reflex custom component AgGrid."""

# For wrapping react guide, visit https://reflex.dev/docs/wrapping-react/overview/

import reflex as rx

import os
from typing import Any
from .datasource import Datasource, SSRMDatasource


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


class AgGrid(rx.Component):
    library: str = "ag-grid-react"
    tag: str = "AgGridReact"

    getRowId: rx.EventHandler[lambda e0: [e0]]
    column_defs: rx.Var[list[dict[str, Any]]]
    row_data: rx.Var[list[dict[str, Any]]]
    treeData: rx.Var[bool] = rx.Var.create_safe(False)
    defaultColDef: rx.Var[dict[str, Any]] = {}
    autoGroupColumnDef: rx.Var[Any] = {}
    pinnedBottomRowData: rx.Var[list[dict[str, Any]]] = []
    groupDefaultExpanded: rx.Var[int] | None = -1
    groupSelectsChildren: rx.Var[bool] = False
    suppressRowClickSelection: rx.Var[bool] = False
    rowSelection: rx.Var[str] = "single"
    animateRows: rx.Var[bool] = False
    getDataPath: rx.EventHandler[lambda e0: [e0]]
    sideBar: rx.Var[str | dict[str, Any] | bool | list[str]] = ""
    groupAllowUnbalanced: rx.Var[bool] = False
    pivotPanelShow: rx.Var[str] = "never"
    rowGroupPanelShow: rx.Var[str] = "never"
    suppressAggFuncInHeader: rx.Var[bool] = False
    groupLockGroupColumns: rx.Var[int] = 0
    maintainColumnOrder: rx.Var[bool] = False

    # infinite/serverside row model
    rowModelType: rx.Var[str]
    cacheBlockSize: rx.Var[int]
    maxBlocksInCache: rx.Var[int]
    rowBuffer: rx.Var[int]
    cacheOverflowSize: rx.Var[int]
    maxConcurrentDatasourceRequests: rx.Var[int]
    infiniteInitialRowCount: rx.Var[int]
    datasource: rx.Var[Datasource]
    isServerSideGroup: rx.EventHandler[lambda e0: [e0]]
    getServerSideGroupKey: rx.EventHandler[lambda e0: [e0]]
    serverSideDatasource: rx.Var[SSRMDatasource]
    isServerSideGroupOpenByDefault: rx.EventHandler[lambda e0: [e0]]
    serverSideEnableClientSideSort: rx.Var[bool] = False
    getChildCount: rx.EventHandler[lambda e0: [e0]]

    # selection events
    onCellClicked: rx.EventHandler[_on_ag_grid_event]
    onSelectionChanged: rx.EventHandler[_on_selection_change_signature]
    onFirstDataRendered: rx.EventHandler[_on_ag_grid_event]

    lib_dependencies: list[str] = [
        "ag-grid-community",
        "ag-grid-enterprise",
    ]

    @classmethod
    def create(
        cls,
        *children,
        id: str,
        data_path_key: str | None = None,
        isServerSideGroupKey: str | None = None,
        getServerSideGroupKey: str | None = None,
        serverSideGroupOpenLevel: int | None = None,
        childCountKey: str | None = None,
        rowIdKey: str | None = None,
        **props,
    ) -> rx.Component:
        props.setdefault("id", id)

        # handle hierarchical data
        if data_path_key is not None:
            props["getDataPath"] = rx.Var.create_safe(
                f"(data) => data.{data_path_key}", _var_is_string=False
            ).to(rx.EventChain)

        if isServerSideGroupKey is not None:
            props["isServerSideGroup"] = rx.Var.create_safe(
                f"(data) => data.{isServerSideGroupKey}", _var_is_string=False
            ).to(rx.EventChain)

        if getServerSideGroupKey is not None:
            props["getServerSideGroupKey"] = rx.Var.create_safe(
                f"(data) => data.{getServerSideGroupKey}", _var_is_string=False
            ).to(rx.EventChain)

        if serverSideGroupOpenLevel is not None:
            props["isServerSideGroupOpenByDefault"] = rx.Var.create_safe(
                f"(params) => params.rowNode.level < {serverSideGroupOpenLevel}",
                _var_is_string=False,
            ).to(rx.EventChain)

        if childCountKey is not None:
            props["getChildCount"] = rx.Var.create_safe(
                f"(data) => data ? data.{childCountKey} : undefined",
                _var_is_string=False,
            ).to(rx.EventChain)

        if rowIdKey is not None:
            props["getRowId"] = rx.Var.create_safe(
                f"(params) => params.data.{rowIdKey}", _var_is_string=False
            ).to(rx.EventChain)

        props["class_name"] = rx.color_mode_cond(
            "ag-theme-quartz", "ag-theme-quartz-dark"
        )

        return super().create(*children, **props)

    def add_imports(self):
        return {
            "": [
                "ag-grid-community/styles/ag-grid.css",
                "ag-grid-community/styles/ag-theme-quartz.css",
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

    def show_now_rows_overlay(self) -> rx.event.EventSpec:
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


ag_grid = AgGrid.create
