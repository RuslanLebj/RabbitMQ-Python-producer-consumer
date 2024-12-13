async def fetch_page(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as e:
        print(f"Ошибка загрузки страницы {url}: {e}")
        return None