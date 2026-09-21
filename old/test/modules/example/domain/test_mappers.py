import pytest

from app.modules.example.domain.entities import Example
from app.modules.example.domain.mappers import example_entity_mapper
from app.modules.example.domain.value_objects import FullName
from app.modules.example.presentation.schemas import ExampleRequest, ExampleResponse


class TestExampleEntityMapper:
    @pytest.mark.asyncio
    async def test_request_to_entity(self):
        req = ExampleRequest(first_name="Jane", last_name="Smith")
        result = await example_entity_mapper(req)
        assert isinstance(result, Example)
        assert str(result.full_name) == "Jane Smith"

    @pytest.mark.asyncio
    async def test_entity_to_response(self):
        ex = Example(full_name=FullName(first_name="Jane", last_name="Smith"))
        result = await example_entity_mapper(ex)
        assert isinstance(result, ExampleResponse)
        assert result.message == "Hello, Jane Smith!"
