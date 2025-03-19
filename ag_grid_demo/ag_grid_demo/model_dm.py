import datetime

import faker
import reflex as rx
from reflex_ag_grid.wrapper import ModelWrapper, model_wrapper
from sqlmodel import Column, DateTime, Field, func


class Friend(rx.Model, table=True):
    name: str
    age: int
    years_known: int
    owes_me: bool = False
    has_a_dog: bool = False
    spouse_is_annoying: bool = False
    met: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    @classmethod
    def generate_fakes(cls, n: int) -> list["Friend"]:
        new_friends = []
        fake = faker.Faker()
        for _ in range(n):
            name = fake.name()
            age = fake.random_int(min=18, max=80)
            years_known = fake.random_int(min=0, max=age)
            new_friends.append(
                Friend(
                    name=name,
                    age=age,
                    years_known=years_known,
                    owes_me=fake.pybool(20),
                    has_a_dog=fake.pybool(60),
                    spouse_is_annoying=fake.pybool(30),
                    met=fake.date_time_between(
                        start_date=f"-{years_known+1}y", end_date=f"-{years_known}y"
                    ),
                ),
            )
        return new_friends


# Basic Example of a ModelWrapper with no customization
@rx.page("/model")
def model_page():
    return rx.box(
        model_wrapper(
            model_class=Friend,
        ),
        width="100vw",
        height="100vh",
    )


# This bogus auth state demonstrates how an extended ModelWrapper can check
# against values in another state before returning/modifying the data.
class AuthState(rx.State):
    _logged_in: bool = False

    @rx.var(cache=True)
    def logged_in(self):
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
        return await super()._get_data(
            start, end, filter_model=filter_model, sort_model=sort_model
        )

    @rx.var(cache=True)
    def selected_items(self) -> list[Friend]:
        # Normally selected items are backend-only, but we can provide
        # a computed var to render them in the UI.
        return self._selected_items


# Advanced example of an extended ModelWrapper with custom behavior
@rx.page("/model-auth")
def model_page_auth():
    grid = FriendModelWrapper.create(
        model_class=Friend,
        row_selection="multiple",
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
        ),
        rx.box(
            grid,
            width="100vw",
            height="90vh",
        ),
    )
