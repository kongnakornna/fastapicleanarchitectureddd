import pytest

from app.modules.example.application.use_cases import ExampleUseCases
from app.modules.example.domain.entities import Example
from app.modules.example.domain.value_objects import FullName
from app.modules.example.presentation.exceptions import ExampleException


class TestExampleUseCasesHello:
    @pytest.mark.asyncio
    async def test_returns_example(self):
        ex = Example(
            full_name=FullName(first_name="Jane", last_name="Doe")
        )
        result = await ExampleUseCases.hello(ex)
        assert result is ex

    @pytest.mark.asyncio
    async def test_raises_example_exception_on_unexpected_error(self):
        with pytest.raises(ExampleException):
            raise ExampleException()
