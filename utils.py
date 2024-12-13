async def fetch_page(session, url):
    """
    Загружает страницу по указанному URL с помощью асинхронного HTTP-запроса.

    :param session: Сессия aiohttp для выполнения HTTP-запроса.
    :param url: URL страницы, которую необходимо загрузить.
    :return: Текст HTML-страницы в случае успешной загрузки, или None в случае ошибки.
    """
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as e:
        print(f"Error fetching page: {url}: {e}")
        return None