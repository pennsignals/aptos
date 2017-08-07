from .primitive import Creator
from .visitor import ResolveVisitor


class Parser:

    @staticmethod
    def parse(schema):
        raise NotImplementedError()


class SchemaParser(Parser):

    @staticmethod
    def parse(schema):
        component = Creator.create(schema.get('type')).unmarshal(schema)
        component.accept(ResolveVisitor(schema))
        return component
