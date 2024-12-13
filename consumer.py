import os
import asyncio
import aiohttp
from dotenv import load_dotenv
import aio_pika
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import logging

from utils import fetch_page

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load RabbitMQ connection details from environment variables
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
QUEUE_NAME = os.getenv("QUEUE_NAME")

TIMEOUT = 10


async def extract_links(html, base_url):
    """
    Извлекает все внутренние ссылки с указанной страницы HTML.

    :param html: HTML-код страницы.
    :param base_url: Базовый URL, который будет использован для формирования абсолютных ссылок.
    :return: Множество внутренних ссылок в формате (URL, текст ссылки).
    """
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        link_text = a_tag.get_text(strip=True) or "No text"
        full_url = urljoin(base_url, href)
        parsed_base = urlparse(base_url)
        parsed_url = urlparse(full_url)
        if parsed_base.netloc == parsed_url.netloc:
            links.add((full_url, link_text))
    return links


async def publish_to_queue(channel, link):
    """
    Публикует ссылку в очередь RabbitMQ.

    :param channel: Канал для отправки сообщения.
    :param link: Ссылка, которую нужно отправить в очередь.
    """
    await channel.default_exchange.publish(
        aio_pika.Message(body=link.encode()),
        routing_key=QUEUE_NAME,
    )


async def process_message(channel, url):
    """
    Обрабатывает сообщение, извлекая ссылки с указанного URL и отправляя их в очередь RabbitMQ.

    :param channel: Канал для отправки сообщений в очередь.
    :param url: URL, с которого нужно извлечь ссылки.
    """
    async with aiohttp.ClientSession() as session:
        html = await fetch_page(session, url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            page_title = soup.title.string.strip() if soup.title else "No title"
            logger.info(f"Processing page: {page_title} ({url})")
            links = await extract_links(html, url)
            for link_url, link_text in links:
                logger.info(f"Found link: {link_text} ({link_url})")
                await publish_to_queue(channel, link_url)


async def consume():
    """
    Подключается к RabbitMQ, ожидает сообщения и обрабатывает их.
    Сообщения содержат URL, по которым необходимо извлечь ссылки и отправить их в очередь.
    """
    connection = await aio_pika.connect_robust(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        login=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD,
    )
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)

        logger.info("Waiting for messages...")

        while True:
            try:
                message = await queue.get(timeout=TIMEOUT)
                async with message.process():
                    url = message.body.decode()
                    await process_message(channel, url)
            except aio_pika.exceptions.QueueEmpty:
                logger.info(f"No messages for {TIMEOUT} seconds. Stopping consumer.")
                break


if __name__ == "__main__":
    asyncio.run(consume())