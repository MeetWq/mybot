import httpx


async def get_nbnhhsh(keyword: str) -> str:
    url = "https://lab.magiconch.com/api/nbnhhsh/guess"
    headers = {"referer": "https://lab.magiconch.com/nbnhhsh/"}
    data = {"text": keyword}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url=url, headers=headers, data=data)
        res = resp.json()
    results = []
    for i in res:
        if "trans" in i and i["trans"]:
            results.append(f"{i['name']} => {'，'.join(i['trans'])}")
    return "\n".join(results)
