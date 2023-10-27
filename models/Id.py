from bson import ObjectId
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import CoreSchema, core_schema
from pydantic.json_schema import JsonSchemaValue
from typing import Any


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(ObjectId))


    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        # Modify the JSON schema as needed
        json_schema["type"] = "string"
        return json_schema

