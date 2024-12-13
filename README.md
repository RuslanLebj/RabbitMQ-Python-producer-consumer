# RabbitMQ Python producer consumer

Два консольных приложения, одно из которых на входе из аргументов командной
строки принимает любой HTTP(S) URL, находит все внутренние ссылки (только для
этого домена) в HTML коде (a[href]), помещает их в очередь RabbitMQ по одной.
Второе приложение - "вечный" асинхронный producer/consumer, который читает из
очереди эти ссылки, также находит внутренние ссылки и помещает в их очередь
## Запуск

1. Клонируйте репозиторий:
 ```bash
 git clone https://github.com/RuslanLebj/RabbitMQ-Python-producer-consumer
 cd RabbitMQ-Python-producer-consumer
 ```


2. Установите необходимые зависимости:
 ```bash
 poetry install
 ```


3. Создайте файл `.env` и скопируйте в него данные из `template.env`, при необходимости измените данные


4. Запустите RabbitMQ в Docker контейнере
    ```bash
       docker-compose up --build -d
    ```
    
5. Запустите producer (передайте URL в качестве аргумента):
   ```bash
   python producer.py <url>
   ```
   
   Пример с Wikipedia:
   ```bash
   python producer.py https://ru.wikipedia.org/wiki/%D0%9D%D0%BE%D0%B2%D1%8B%D0%B9_%D0%B3%D0%BE%D0%B4
   ```


6. Запустите consumer:
 ```bash
   python consumer.py
 ```
