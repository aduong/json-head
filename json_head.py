from sanic import Sanic
from sanic import response
import aiohttp
import asyncio
import re
import json

app = Sanic(__name__)

INDEX = """<!DOCTYPE html>
<title>json-head</title>
<h1>json-head</h1>
<p>JSON (and JSON-P) API for running a HEAD request against a URL.
<ul>
    <li><a href="/?url=http://www.google.com/">/?url=http://www.google.com/</a>
    <li><a href="/?url=http://www.yahoo.com/&amp;callback=foo">/?url=http://www.yahoo.com/&amp;callback=foo</a>
    <li><a href="/?url=https://www.google.com/&amp;url=http://www.yahoo.com/">/?url=https://www.google.com/&amp;url=http://www.yahoo.com/</a>
</ul>
"""

callback_re = re.compile(r'^[a-zA-Z_](\.?[a-zA-Z0-9_]+)+$')
is_valid_callback = callback_re.match


async def head(session, url):
    try:
        async with session.head(url) as response:
            return {
                'ok': True,
                'headers': dict(response.headers),
                'status': response.status,
                'url': url,
            }
    except Exception as e:
        return {
            'ok': False,
            'error': str(e),
            'url': url,
        }


@app.route('/')
async def handle_request(request):
    urls = request.args.getlist('url')
    callback = request.args.get('callback')
    if urls:
        async with aiohttp.ClientSession() as session:
            head_infos = await asyncio.gather(*[
                asyncio.Task(head(session, url)) for url in urls
            ])
            if callback and is_valid_callback(callback):
                return response.text(
                    '{}({})'.format(callback, json.dumps(head_infos, indent=2)),
                    content_type='application/javascript',
                    headers={'Access-Control-Allow-Origin': '*'},
                )
            else:
                return response.json(
                    head_infos,
                    headers={'Access-Control-Allow-Origin': '*'},
                )
    else:
        return response.html(INDEX)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8006)