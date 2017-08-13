from .model import OpenAPI
from .visitor import OpenAPIResolveVisitor
from ...parser import Parser


class OpenAPIParser(Parser):

    @staticmethod
    def parse(schema):
        component = OpenAPI.unmarshal(schema)
        component.accept(OpenAPIResolveVisitor(schema))
        return component
