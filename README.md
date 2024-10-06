# Python Web
**Студент:** Илья Тамбовцев - [телега](https://t.me/ilchos)

Здесь будут лежать мои домашние задания по курсу "Web Python"

## Как запускать?
- Для установки зависимостей `poetry install`
- Для запуска тестов `./hw<NN>/tests/run.sh` -- если он есть
- Во вкладке `Actions` результаты тестов через CI

## Домашние задания
[Репа Курса](https://github.com/katunilya/hse-python-backend/)

Тесты кладу в папки с домашками. CI запускает тесты для последней домашки.

### ДЗ 1 математический сервер
[Описание ДЗ](https://github.com/katunilya/hse-python-backend/tree/main?tab=readme-ov-file#%D0%BB%D0%B5%D0%BA%D1%86%D0%B8%D1%8F-1---%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D1%8B-%D1%81%D0%B5%D1%82%D0%B8-%D0%B8-python-backend) - [Папка hw01](https://github.com/tambovtsev-io/python_web/tree/master/hw01)

#### Запуск
- быстрый запуск `./tests/run.sh` (сервер + тесты)
- запуск сервера с математическими операциями: `poetry run python simple_math_asgi.py`
- запуск тестов `poetry run pytest test_hw01.py`. тесты брал из репозитория курса [ссылка](https://github.com/katunilya/hse-python-backend/blob/main/tests/test_homework_1.py)

### ДЗ 2 API Корзины
[Описание hw02](https://github.com/katunilya/hse-python-backend/tree/main/lecture_2/hw)
