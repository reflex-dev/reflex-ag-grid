import asyncio
import json
import reflex as rx

from fastapi import HTTPException

from reflex_ag_grid.wrapper import ModelWrapper

from .common import demo
from .model_wrapper_simple import Friend


# This bogus auth state demonstrates how an extended ModelWrapper can check
# against values in another state before returning/modifying the data.
class AuthState(rx.State):
    _logged_in: bool = False

    @rx.var(cache=True)
    def logged_in(self) -> bool:
        return self._logged_in

    def toggle_login(self):
        self._logged_in = not self._logged_in
        return self._refresh_grid()

    def _refresh_grid(self):
        return [cls.on_mount for cls in FriendModelWrapper.__subclasses__()]

    def generate_friends(self, n: int):
        """If only it were that easy..."""
        if not self._logged_in:
            return rx.toast.error("You must be logged in to generate friends.")
        with rx.session() as session:
            for f in Friend.generate_fakes(n):
                session.add(f)
            session.commit()
        return [
            rx.toast.info(f"Created {n} friends."),
            *self._refresh_grid(),
        ]


class GridState(rx.State):
    column_state_json: str = rx.LocalStorage()

    @rx.event
    def save_column_state(self, state: list):
        self.column_state_json = json.dumps(state)

    @rx.var
    def column_state(self) -> list:
        try:
            return json.loads(self.column_state_json)
        except ValueError:
            return []

# When extending a ModelWrapper, you can override methods to customize the behavior.
class FriendModelWrapper(ModelWrapper[Friend]):
    def _get_column_defs(self):
        """In this example, we remove the ability to filter and sort a particular field."""
        cols = super()._get_column_defs()
        for col in cols:
            if col.field == "spouse_is_annoying":
                col.filter = False
                col.sortable = False
        return cols

    async def on_value_setter(self, row_data, field_name, value):
        auth_state = await self.get_state(AuthState)
        if not auth_state.logged_in:
            return  # no modification for logged out users
        return super().on_value_setter(row_data, field_name, value)

    async def _get_data(self, start, end, filter_model, sort_model):
        auth_state = await self.get_state(AuthState)
        if not auth_state.logged_in:
            return []  # no records for logged out users
        await asyncio.sleep(0.2)
        if end < 150:
            return await super()._get_data(
                start, end, filter_model=filter_model, sort_model=sort_model
            )
        else:
            raise HTTPException(status_code=400, detail="Too many rows requested.")

    @rx.var(cache=True)
    def selected_items(self) -> list[Friend]:
        # Normally selected items are backend-only, but we can provide
        # a computed var to render them in the UI.
        return self._selected_items


# Advanced example of an extended ModelWrapper with custom behavior
@demo(
    route="/model-auth",
    title="Customized ModelWrapper",
    description="Extended infinite-row ModelWrapper with custom behavior and auth.",
)
def model_page_auth():
    grid = FriendModelWrapper.create(
        model_class=Friend,
        row_selection="multiple",
        custom_attrs={
            "loading_cell_renderer": rx.vars.function.ArgsFunctionOperation.create(
                args_names=("params",),
                return_expr=rx.Var.create(
                    rx.box(
                        rx.cond(
                            rx.Var("params.node.failedLoad"),
                            rx.hstack(rx.icon("x"), rx.text("Failed to load rows: ", rx.Var("params.node.parent.failReason"), align="center")),
                            rx.hstack(rx.spinner(), rx.text("Loading rows..."), align="center"),
                        ),
                        padding_x="5px",
                    ),
                ),
            ),
        }
    )
    return rx.vstack(
        rx.hstack(
            rx.cond(
                AuthState.logged_in,
                rx.button("Logout", on_click=AuthState.toggle_login),
                rx.button("Login", on_click=AuthState.toggle_login),
            ),
            rx.cond(
                AuthState.logged_in,
                rx.button("Generate Friends", on_click=AuthState.generate_friends(50)),
            ),
            rx.foreach(
                grid.State.selected_items,
                lambda friend: rx.badge(friend.name),
            ),
            rx.spacer(),
            rx.button(
                "Save column state",
                on_click=grid.api.get_column_state(callback=GridState.save_column_state),
            ),
            rx.button(
                "Load column state",
                on_click=grid.api.apply_column_state({"state": GridState.column_state}),
            ),
        ),
        rx.box(
            grid,
            width="100%",
            height="65vh",
            padding_bottom="60px",  # for scroll bar and controls
        ),
    )
