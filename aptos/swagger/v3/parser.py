from .model import Swagger
from .visitor import OpenAPIResolveVisitor
from ...parser import Parser


class OpenAPIParser(Parser):

    @staticmethod
    def parse(schema):
        component = Swagger.unmarshal(schema)
        component.accept(OpenAPIResolveVisitor(schema))
        return component
