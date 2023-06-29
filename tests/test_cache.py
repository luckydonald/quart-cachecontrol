import unittest

import pytest
from quart import Quart, Response
from quart_cachecontrol import cache_for, cache, dont_cache, ResponseIsSuccessful, ResponseIsSuccessfulOrRedirect, \
    Always

app = Quart(__name__)

CACHE_SECONDS = 300
VARY_HEADERS = ['User-Agent', 'Referer']
VARY_HEADERS_STR = ','.join(VARY_HEADERS)


@app.route('/cache_for/on_success/<int:status_code>')
@cache_for(only_if=ResponseIsSuccessful, seconds=CACHE_SECONDS)
async def view_cache_for_on_success(status_code):
    return Response(status=status_code)


@app.route('/cache_for/on_success_or_redirect/<int:status_code>')
@cache_for(only_if=ResponseIsSuccessfulOrRedirect, seconds=CACHE_SECONDS)
async def view_cache_for_on_success_or_redirect(status_code):
    return Response(status=status_code)


@app.route('/cache_for/always/<int:status_code>')
@cache_for(only_if=Always, seconds=CACHE_SECONDS)
async def view_cache_for_always(status_code):
    return Response(status=status_code)


@app.route('/cache_for/vary/<int:status_code>')
@cache_for(only_if=ResponseIsSuccessful, seconds=CACHE_SECONDS, vary=VARY_HEADERS)
async def view_cache_for_on_success_with_vary(status_code):
    return Response(status=status_code)


@app.route('/dont_cache/always/<int:status_code>')
@dont_cache(only_if=Always)
async def view_dont_cache_always(status_code):
    return Response(status=status_code)


@app.route('/dont_cache/on_success/<int:status_code>')
@dont_cache(only_if=ResponseIsSuccessful)
async def view_dont_cache_on_success(status_code):
    return Response(status=status_code)


@app.route('/dont_cache/on_success_or_redirect/<int:status_code>')
@dont_cache(only_if=ResponseIsSuccessfulOrRedirect)
async def view_dont_cache_on_success_or_redirect(status_code):
    return Response(status=status_code)


@app.route('/cache/always/<int:status_code>')
@cache(no_store=True, only_if=Always)
async def view_cache_always(status_code):
    return Response(status=status_code)


@app.route('/cache/on_success/<int:status_code>')
@cache(no_store=True, only_if=ResponseIsSuccessful)
async def view_cache_on_success(status_code):
    return Response(status=status_code)


@app.route('/cache/on_success_or_redirect/<int:status_code>')
@cache(no_store=True, only_if=ResponseIsSuccessfulOrRedirect)
async def view_cache_on_success_or_redirect(status_code):
    return Response(status=status_code)


@app.route('/cache/vary/<int:status_code>')
@cache(no_store=True, only_if=ResponseIsSuccessful, vary=VARY_HEADERS)
async def view_cache_on_success_with_vary(status_code):
    return Response(status=status_code)



class TestCacheForAlways(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/always/200')
        # end with
        assert 'Cache-Control' in rv.headers and rv.headers['Cache-Control'] == f'max-age={CACHE_SECONDS}'
        assert 'Expires' in rv.headers

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/always/404')
        # end with
        assert 'Cache-Control' in rv.headers and rv.headers['Cache-Control'] == f'max-age={CACHE_SECONDS}'
        assert 'Expires' in rv.headers


class TestCacheForOnlyOnSuccess(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success/200')
        assert 'Cache-Control' in rv.headers

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success/300')
        assert 'Cache-Control' not in rv.headers

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success/404')
        assert 'Cache-Control' not in rv.headers


class TestCacheForOnlyOnSuccessOrRedirect(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success_or_redirect/200')
        assert 'Cache-Control' in rv.headers

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success_or_redirect/300')
        assert 'Cache-Control' in rv.headers

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success_or_redirect/404')
        assert 'Cache-Control' not in rv.headers


class TestCacheForVary(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success_wo_vary(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success/200')
        assert 'Vary' not in rv.headers

    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/vary/200')
        assert rv.headers.get('Vary') == VARY_HEADERS_STR

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/vary/300')
        assert rv.headers.get('Vary') == VARY_HEADERS_STR

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/vary/404')
        assert rv.headers.get('Vary') == VARY_HEADERS_STR

    @pytest.mark.asyncio
    async def test_server_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/vary/500')
        assert rv.headers.get('Vary') == VARY_HEADERS_STR


class TestDontCacheAlways(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/always/200')
        assert 'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/always/300')
        assert 'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/always/404')
        assert 'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']


class TestDontCacheOnlyOnSuccess:
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success/200')
        assert 'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success/300')
        assert 'Cache-Control' not in rv.headers

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success/404')
        assert 'Cache-Control' not in rv.headers


class TestDontCacheOnlyOnSuccessOrRedirect:
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success_or_redirect/200')
        assert 'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success_or_redirect/300')
        assert 'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success_or_redirect/404')
        assert 'Cache-Control' not in rv.headers


class TestCacheAlways:
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/always/200')
        assert 'Cache-Control' in rv.headers \
               and 'no-store' in rv.headers['Cache-Control'] \
               and 'no-cache' not in rv.headers['Cache-Control']

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/always/300')
        assert 'Cache-Control' in rv.headers \
               and 'no-store' in rv.headers['Cache-Control'] \
               and 'no-cache' not in rv.headers['Cache-Control']

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/always/404')
        assert 'Cache-Control' in rv.headers \
               and 'no-store' in rv.headers['Cache-Control'] \
               and 'no-cache' not in rv.headers['Cache-Control']


class TestCacheOnlyOnSuccess:
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success/200')
        assert 'Cache-Control' in rv.headers \
               and 'no-store' in rv.headers['Cache-Control'] \
               and 'no-cache' not in rv.headers['Cache-Control']

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success/300')
        assert 'Cache-Control' not in rv.headers

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success/404')
        assert 'Cache-Control' not in rv.headers


class TestCacheOnlyOnSuccessOrRedirect:
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success_or_redirect/200')
        assert 'Cache-Control' in rv.headers \
               and 'no-store' in rv.headers['Cache-Control'] \
               and 'no-cache' not in rv.headers['Cache-Control']

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success_or_redirect/300')
        assert 'Cache-Control' in rv.headers \
               and 'no-store' in rv.headers['Cache-Control'] \
               and 'no-cache' not in rv.headers['Cache-Control']

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success_or_redirect/404')
        assert 'Cache-Control' not in rv.headers


class TestCacheVary:
    @pytest.mark.asyncio
    async def test_success_wo_vary(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success/200')
        assert 'Vary' not in rv.headers

    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/vary/200')
        assert rv.headers.get('Vary') == VARY_HEADERS_STR

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/vary/300')
        assert rv.headers.get('Vary') == VARY_HEADERS_STR

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/vary/404')
        assert rv.headers.get('Vary') == VARY_HEADERS_STR

    @pytest.mark.asyncio
    async def test_server_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/vary/500')
        assert rv.headers.get('Vary') == VARY_HEADERS_STR
