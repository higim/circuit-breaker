import pytest

from breaker import CircuitBreaker, OpenCircuitException

@pytest.mark.asyncio
async def test_circuit_breaker_exists():
    cb = CircuitBreaker()

    @cb
    async def call_api():
        return "ok"

    assert await call_api() == "ok"
    assert cb.state == CircuitBreaker.CircuitState.CLOSED


@pytest.mark.asyncio
async def test_circuit_breaker_return_error_while_max_errors_is_not_reached():
    cb = CircuitBreaker(max_consecutive_errors=5)

    @cb
    async def call_api_ko():
        raise Exception()
    
    with pytest.raises(Exception) as excinfo:
        await call_api_ko()
    
    assert not isinstance(excinfo.value, OpenCircuitException)

@pytest.mark.asyncio
async def test_circuit_breaker_return_open_circuit_after_max_errors():
    max_errors = 5
    cb = CircuitBreaker(max_consecutive_errors=max_errors)

    @cb
    async def call_api_ko():
        raise Exception()
    
    for _ in range(max_errors):
        with pytest.raises(Exception) as excinfo:
            await call_api_ko()
        assert not isinstance(excinfo.value, OpenCircuitException)

    with pytest.raises(OpenCircuitException) as excinfo:
        assert await call_api_ko()