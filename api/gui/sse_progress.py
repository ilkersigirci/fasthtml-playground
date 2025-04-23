from asyncio import sleep

from fasthtml.common import (
    Div,
    EventStream,
    P,
    Progress,
    Script,
    Titled,
    fast_app,
    signal_shutdown,
    sse_message,
)
from loguru import logger

hdrs = (Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),)
app, rt = fast_app(hdrs=hdrs)

MAX_VALUE = 100


@rt
def index():
    return Titled(
        "SSE Random Number Generator",
        P("Generate pairs of random numbers, as the list grows scroll downwards."),
        Div(
            hx_ext="sse",
            sse_connect="/number-stream",
            hx_swap="innerHTML",
            sse_swap="message",
        ),
    )


shutdown_event = signal_shutdown()


async def number_generator():
    data = 0
    while not shutdown_event.is_set() and data < MAX_VALUE:
        logger.info(f"Sending data: {data}")
        data += 1
        send_data = Progress(value=data, max=MAX_VALUE)
        yield sse_message(send_data)
        await sleep(0.1)


@rt("/number-stream")
async def get():
    return EventStream(number_generator())
