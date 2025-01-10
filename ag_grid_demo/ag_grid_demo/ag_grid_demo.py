import reflex as rx

from .common import demo, DemoState


@demo(
    route="/",
    title="AG Grid Demo",
    description="A collection of examples using AG Grid in Reflex.",
)
def index():
    return rx.flex(
        rx.foreach(
            DemoState.pages,
            lambda page: rx.card(
                rx.vstack(
                    rx.link(page.title, href=page.route),
                    rx.text(page.description),
                ),
                width="300px",
            ),
        ),
        wrap="wrap",
        spacing="3",
    )


# Add state and page to the app.
app = rx.App()
app.add_page(index)
