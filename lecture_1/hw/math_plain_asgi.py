from typing import Any, Awaitable, Callable


def factorial(n: int) -> int:
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


def fib(n: int) -> int:
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return b


def mean(list: [float]) -> float:
    return sum(list) / len(list)


async def send_error(send, errorCode: int):
    await send({
        "type": "http.response.start",
        "status": errorCode,
        "headers": [
            [b"content-type", b"text/plain"],
        ]
    })
    await send({
        "type": "http.response.body",
        "body": f'{{"result": ERROR {errorCode}}}'.encode(),
    })


async def send_200_answer(send, body=""):
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [
            [b"content-type", b"text/plain"],
        ]
    })
    await send({
        "type": "http.response.body",
        "body": f'{{"result": {body}}}'.encode(),
    })


async def app(
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    assert scope["type"] == "http"

    if scope["method"] != "GET":
        await send_error(send, 404)
        return

    if scope["path"] == "/factorial":
        query_string = scope["query_string"]

        if not query_string.startswith(b'n='):
            await send_error(send, 422)
            return
        value = query_string[2:].decode()

        try:
            value = int(value)
        except Exception as e:
            await send_error(send, 422)
            return

        if value < 0:
            await send_error(send, 400)
            return

        ans = factorial(int(value))
        await send_200_answer(send, ans)
        return

    if scope["path"].startswith("/fibonacci"):
        value = scope["path"][11:]

        try:
            value = int(value)
        except Exception as e:
            await send_error(send, 422)
            return

        if value < 0:
            await send_error(send, 400)
            return

        ans = fib(value)
        await send_200_answer(send, ans)
        return

    if scope["path"] == "/mean":
        raw_body = await receive()
        body = raw_body["body"].decode()

        try:
            body = list(map(lambda x: float(x), list(eval(body))))
        except Exception as e:
            await send_error(send, 422)
            return

        if len(body) == 0:
            await send_error(send, 400)
            return
        ans = mean(body)
        await send_200_answer(send, ans)
        return

    await send_error(send, 404)
