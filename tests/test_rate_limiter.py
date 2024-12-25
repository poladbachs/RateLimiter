import pytest
import asyncio
from rate_limiter import AsyncRateLimiter, RateLimiterGroup

@pytest.mark.asyncio
async def test_async_rate_limiter():
    limiter = AsyncRateLimiter(period_sec=1, max_calls=3)
    
    async def make_request():
        await limiter.acquire()
        return "success"
    
    results = await asyncio.gather(make_request(), make_request(), make_request())
    assert results == ["success", "success", "success"]

    # Fourth call should be delayed
    start_time = asyncio.get_event_loop().time()
    await make_request()
    end_time = asyncio.get_event_loop().time()
    assert end_time - start_time >= 1  # Ensure 1-second delay

@pytest.mark.asyncio
async def test_rate_limiter_group():
    limits = [
        {'tag': 'test', 'period_sec': 1, 'count': 2},
        {'tag': 'test2', 'period_sec': 2, 'count': 3},
    ]
    group = RateLimiterGroup(limits)

    async def make_request(tags):
        await group.rate_limit(tags)
        return "success"

    # Test individual tags
    results = await asyncio.gather(make_request(['test']), make_request(['test']))
    assert results == ["success", "success"]

    # Third request should wait for the next period
    start_time = asyncio.get_event_loop().time()
    await make_request(['test'])
    end_time = asyncio.get_event_loop().time()
    assert end_time - start_time >= 1  # Ensure 1-second delay
