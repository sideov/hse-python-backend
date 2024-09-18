**Для запуска первой домашки необходимо прописать в консоли uvicorn homework_1.hw1:app. После этого можно запустить тесты**


# Python Backend

- [Репозиторий с примерами](https://github.com/katunilya/hse-python-backend) -
  вы уже тут
- [Лекции в
Miro](https://miro.com/app/board/uXjVKkM4JvE=/?share_link_id=92562179702) (все
лекции будут постепенно заливаться в эту доску)
- [Лекции в
  pdf](https://drive.google.com/drive/folders/1m1Qmgz5ncP1LWLmuhcZgBQBY730qKxb4?usp=sharing)
  (так же будут постепенно подгружаться)
- [Оценки](https://docs.google.com/spreadsheets/d/1BeY-p-UYCfBX-KBN50pxWOykYKlTydoPF4lIXlVHZvs/edit?usp=sharing)

## ДЗ

Для сдачи ДЗ не забудьте приложить ссылку на репозиторий в таблицу с
[Оценками](https://docs.google.com/spreadsheets/d/1BeY-p-UYCfBX-KBN50pxWOykYKlTydoPF4lIXlVHZvs/edit?usp=sharing).
Если хотите сделать репозиторий приватным, то не забудьте пригласить -
`katunilya` (GH/GL). Сдавать можно в несколько итераций, главное - заранее (не
день в день).

### Лекция 1 - Основы сети и Python Backend

Реализовать "Математическое API" из примера напрямую через ASGI-compatible
функцию. В частности

- запросы, для которых нет обработчиков (не тот метод, не тот путь) должны
  возвращать ошибку `404 Not Found`
- запрос `GET /factorial` (n!)
  - возвращается в тело запроса в формате json вида `{"result": 123}`
  - в query-параметре запроса должен быть параметр `n: int`
  - если параметра нет, или он не является числом - возвращаем `422
    Unprocessable Entity`
  - если параметр не валидное число (меньше 0) - возвращаем `400 Bad Request`
- запрос `GET /fibonacci` (n-ое число fibonacci)
  - возвращается в тело запроса в формате json вида `{"result": 123}`
  - в path-параметре запроса (`fibonacci/{n}`) должен быть параметр `n: int`
  - если параметра нет, или он не является числом - возвращаем `422
    Unprocessable Entity`
  - если параметр не валидное число (меньше 0) - возвращаем `400 Bad Request`
- запрос `GET /mean` (среднее массива)
  - возвращается в тело запроса в формате json вида `{"result": 123}`
  - в теле запроса не пустой массив из `float`'ов (например `[1, 2.3, 3.6]`)
  - тело не является массивом `float`'ов - возвращаем `422
    Unprocessable Entity`
  - если массив пустой - возвращаем `400 Bad Request`

Болванка для начала:

```python
async def app(scope, receive, send) -> None:
    ...
```

В репозитории так же должна быть организована работа с зависимостями (хотя бы
`requirements.txt`).

Стоит так же заранее прописать (в коде или `README.md`), как запустить
приложение (например: `uvicorn main:app`).

- [Спецификация ASGI](https://asgi.readthedocs.io/en/latest/specs/www.html#http)
- [Исходный код API на FastAPI](/lecture_1/math_example.py)
- [Тесты для первого ДЗ (pytest)](/tests/test_homework_1.py)

Чтобы протестировать свое ДЗ или работу примера на FastAPI - в одном терминале
запустите приложение (например `uvicorn lecture_1.math_example:app`), а в другом
выполните `pytest`.
