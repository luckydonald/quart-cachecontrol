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
        self.assertEqual(f'max-age={CACHE_SECONDS}', 'Cache-Control' in rv.headers and rv.headers['Cache-Control'], "f'max-age={CACHE_SECONDS}' == 'Cache-Control' in rv.headers and rv.headers['Cache-Control']")
        self.assertIn('Expires', rv.headers, "'Expires' in rv.headers")

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/always/404')
        # end with
        self.assertEqual(f'max-age={CACHE_SECONDS}', 'Cache-Control' in rv.headers and rv.headers['Cache-Control'], "f'max-age={CACHE_SECONDS}' == 'Cache-Control' in rv.headers and rv.headers['Cache-Control']")
        self.assertIn('Expires', rv.headers, "'Expires' in rv.headers")


class TestCacheForOnlyOnSuccess(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success/200')
        self.assertIn('Cache-Control', rv.headers, "'Cache-Control' in rv.headers")

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success/300')
        self.assertNotIn('Cache-Control', rv.headers, "'Cache-Control' not in rv.headers")

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success/404')
        self.assertNotIn('Cache-Control', rv.headers, "'Cache-Control' not in rv.headers")


class TestCacheForOnlyOnSuccessOrRedirect(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success_or_redirect/200')
        self.assertIn('Cache-Control', rv.headers, "'Cache-Control' in rv.headers")

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success_or_redirect/300')
        self.assertIn('Cache-Control', rv.headers, "'Cache-Control' in rv.headers")

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success_or_redirect/404')
        self.assertNotIn('Cache-Control', rv.headers, "'Cache-Control' not in rv.headers")


class TestCacheForVary(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success_wo_vary(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/on_success/200')
        self.assertNotIn('Vary', rv.headers, "'Vary' not in rv.headers")

    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/vary/200')
        self.assertEqual(VARY_HEADERS_STR, rv.headers.get('Vary'), "VARY_HEADERS_STR == rv.headers.get('Vary')")

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/vary/300')
        self.assertEqual(VARY_HEADERS_STR, rv.headers.get('Vary'), "VARY_HEADERS_STR == rv.headers.get('Vary')")

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/vary/404')
        self.assertEqual(VARY_HEADERS_STR, rv.headers.get('Vary'), "VARY_HEADERS_STR == rv.headers.get('Vary')")

    @pytest.mark.asyncio
    async def test_server_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache_for/vary/500')
        self.assertEqual(VARY_HEADERS_STR, rv.headers.get('Vary'), "VARY_HEADERS_STR == rv.headers.get('Vary')")


class TestDontCacheAlways(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/always/200')
        self.assertIn('Cache-Control' in rv.headers and 'no-cache', rv.headers['Cache-Control'], "'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']")

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/always/300')
        self.assertIn('Cache-Control' in rv.headers and 'no-cache', rv.headers['Cache-Control'], "'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']")

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/always/404')
        self.assertIn('Cache-Control' in rv.headers and 'no-cache', rv.headers['Cache-Control'], "'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']")


class TestDontCacheOnlyOnSuccess(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success/200')
        self.assertIn('Cache-Control' in rv.headers and 'no-cache', rv.headers['Cache-Control'], "'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']")

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success/300')
        self.assertNotIn('Cache-Control', rv.headers, "'Cache-Control' not in rv.headers")

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success/404')
        self.assertNotIn('Cache-Control', rv.headers, "'Cache-Control' not in rv.headers")


class TestDontCacheOnlyOnSuccessOrRedirect(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success_or_redirect/200')
        self.assertIn('Cache-Control' in rv.headers and 'no-cache', rv.headers['Cache-Control'], "'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']")

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success_or_redirect/300')
        self.assertIn('Cache-Control' in rv.headers and 'no-cache', rv.headers['Cache-Control'], "'Cache-Control' in rv.headers and 'no-cache' in rv.headers['Cache-Control']")

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/dont_cache/on_success_or_redirect/404')
        self.assertNotIn('Cache-Control', rv.headers, "'Cache-Control' not in rv.headers")


class TestCacheAlways(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/always/200')
        self.assertIn('Cache-Control', rv.headers, "'Cache-Control' in rv.headers")
        self.assertIn('no-store', rv.headers['Cache-Control'], "'no-store' in rv.headers['Cache-Control']")
        self.assertNotIn('no-cache', rv.headers['Cache-Control'], "'no-cache' not in rv.headers['Cache-Control']")

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/always/300')
        self.assertIn('Cache-Control', rv.headers, "'Cache-Control' in rv.headers")
        self.assertIn('no-store', rv.headers['Cache-Control'], "'no-store' in rv.headers['Cache-Control']")
        self.assertNotIn('no-cache', rv.headers['Cache-Control'], "'no-cache' not in rv.headers['Cache-Control']")

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/always/404')
        self.assertIn('Cache-Control', rv.headers, "'Cache-Control' in rv.headers")
        self.assertIn('no-store', rv.headers['Cache-Control'], "'no-store' in rv.headers['Cache-Control']")
        self.assertNotIn('no-cache', rv.headers['Cache-Control'], "'no-cache' not in rv.headers['Cache-Control']")


class TestCacheOnlyOnSuccess(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success/200')
        self.assertIn('Cache-Control', rv.headers, "'Cache-Control' in rv.headers")
        self.assertIn('no-store', rv.headers['Cache-Control'], "'no-store' in rv.headers['Cache-Control']")
        self.assertNotIn('no-cache', rv.headers['Cache-Control'], "'no-cache' not in rv.headers['Cache-Control']")

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success/300')
        self.assertNotIn('Cache-Control', rv.headers, "'Cache-Control' not in rv.headers")

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success/404')
        self.assertNotIn('Cache-Control', rv.headers, "'Cache-Control' not in rv.headers")


class TestCacheOnlyOnSuccessOrRedirect(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success_or_redirect/200')
        self.assertIn('Cache-Control', rv.headers, "'Cache-Control' in rv.headers")
        self.assertIn('no-store', rv.headers['Cache-Control'], "'no-store' in rv.headers['Cache-Control']")
        self.assertNotIn('no-cache', rv.headers['Cache-Control'], "'no-cache' not in rv.headers['Cache-Control']")

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success_or_redirect/300')
        self.assertIn('Cache-Control', rv.headers , "'Cache-Control' in rv.headers")
        self.assertIn('no-store', rv.headers['Cache-Control'], "'no-store' in rv.headers['Cache-Control']")
        self.assertNotIn('no-cache', rv.headers['Cache-Control'], "'no-cache' not in rv.headers['Cache-Control']")

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success_or_redirect/404')
        self.assertNotIn('Cache-Control', rv.headers, "'Cache-Control' not in rv.headers")


class TestCacheVary(unittest.IsolatedAsyncioTestCase):
    @pytest.mark.asyncio
    async def test_success_wo_vary(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/on_success/200')
        self.assertNotIn('Vary', rv.headers, "'Vary' not in rv.headers")

    @pytest.mark.asyncio
    async def test_success(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/vary/200')
        self.assertEqual(VARY_HEADERS_STR, rv.headers.get('Vary'), "VARY_HEADERS_STR == rv.headers.get('Vary')")

    @pytest.mark.asyncio
    async def test_redirect(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/vary/300')
        self.assertEqual(VARY_HEADERS_STR, rv.headers.get('Vary'), "VARY_HEADERS_STR == rv.headers.get('Vary')")

    @pytest.mark.asyncio
    async def test_client_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/vary/404')
        self.assertEqual(VARY_HEADERS_STR, rv.headers.get('Vary'), "VARY_HEADERS_STR == rv.headers.get('Vary')")

    @pytest.mark.asyncio
    async def test_server_error(self):
        async with app.test_client() as client:
            rv = await client.get('/cache/vary/500')
        self.assertEqual(VARY_HEADERS_STR, rv.headers.get('Vary'), "VARY_HEADERS_STR == rv.headers.get('Vary')")
