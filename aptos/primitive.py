import re

from copy import deepcopy


class Component:

    def accept(self, visitor, *args):
        raise NotImplementedError()


class Creator:

    @staticmethod
    def create(identifier):
        return {
            str: lambda identifier: {
                'boolean': Boolean,
                'null': Null,
                'integer': Integer,
                'number': Number,
                'string': String,
                'array': Array,
                'object': Object,
            }.get(identifier, UnkownHandler),
            list: lambda identifier: Union,
            type(None): lambda identifier: UnkownHandler,
        }[identifier.__class__](identifier)


class Translator:

    @staticmethod
    def translate(instance):
        return {
            bool: Boolean,
            type(None): Null,
            int: Integer,
            float: Number,
            str: String,
            list: Array,
            dict: Object,
        }[instance.__class__]


class SchemaArray(Component, list):

    @classmethod
    def unmarshal(cls, schema):
        return cls(
            Creator.create(element.get('type')).unmarshal(element)
            for element in schema)


class AllOf(SchemaArray):

    def accept(self, visitor, *args):
        return visitor.visit_all_of(self, *args)


class AnyOf(SchemaArray):

    def accept(self, visitor, *args):
        return visitor.visit_any_of(self, *args)


class OneOf(SchemaArray):

    def accept(self, visitor, *args):
        return visitor.visit_one_of(self, *args)


class Primitive(Component):

    def __init__(self, enum=None, const=None, type=None, allOf=None,
                 anyOf=None, oneOf=None, definitions=None, title='',
                 description='', default=None, examples=None, **kwargs):
        self.enum = [] if enum is None else list(set(enum))
        self.const = const
        self.type = type
        self.allOf = AllOf() if allOf is None else allOf
        self.anyOf = AnyOf() if anyOf is None else anyOf
        self.oneOf = OneOf() if oneOf is None else oneOf
        self.definitions = Definitions() if definitions is None else definitions  # noqa: E501
        self.title = title
        self.description = description
        self.default = default
        self.examples = [] if examples is None else list(examples)

    @classmethod
    def unmarshal(cls, schema):
        schema = deepcopy(schema)
        schema['allOf'] = AllOf.unmarshal(schema.get('allOf', []))
        schema['anyOf'] = AnyOf.unmarshal(schema.get('anyOf', []))
        schema['oneOf'] = OneOf.unmarshal(schema.get('oneOf', []))
        schema['definitions'] = Definitions.unmarshal(
            schema.get('definitions', {}))
        return cls(**schema)

    def accept(self, visitor, *args):
        return visitor.visit_primitive(self, *args)


class EmptySchema(Primitive):

    """An empty schema is a JSON Schema with no properties, or only
    unknown properties.
    """

    def accept(self, visitor, *args):
        return visitor.visit_empty_schema(self, *args)


class Enumeration(Primitive):

    def accept(self, visitor, *args):
        return visitor.visit_enumeration(self, *args)


class Boolean(Primitive):

    def accept(self, visitor, *args):
        return visitor.visit_boolean(self, *args)


class Null(Primitive):

    def accept(self, visitor, *args):
        return visitor.visit_null(self, *args)


class NumericType(Primitive):

    def __init__(self, multipleOf=1, maximum=None, exclusiveMaximum=None,
                 minimum=None, exclusiveMinimum=None, **kwargs):
        if multipleOf < 1:
            raise ValueError('The value of "multipleOf" MUST be a number, strictly greater than 0.')  # noqa: E501
        super().__init__(**kwargs)
        self.multipleOf = multipleOf
        self.maximum = maximum
        self.exclusiveMaximum = exclusiveMaximum
        self.minimum = minimum
        self.exclusiveMinimum = exclusiveMinimum


class Integer(NumericType):

    def accept(self, visitor, *args):
        return visitor.visit_integer(self, *args)


class Number(NumericType):

    def accept(self, visitor, *args):
        return visitor.visit_number(self, *args)


class String(Primitive):

    def __init__(self, maxLength=0, minLength=0, pattern='', **kwargs):
        super().__init__(**kwargs)
        self.maxLength = maxLength
        self.minLength = minLength
        self.pattern = pattern

    def accept(self, visitor, *args):
        return visitor.visit_string(self, *args)


class Array(Primitive):

    def __init__(self, items=None, additionalItems=None, maxItems=0,
                 minItems=0, uniqueItems=False, contains=None, **kwargs):
        super().__init__(**kwargs)
        self.items = EmptySchema() if items is None else items
        self.additionalItems = EmptySchema() if additionalItems is None else additionalItems  # noqa: E501
        self.maxItems = maxItems
        self.minItems = minItems
        self.uniqueItems = uniqueItems
        self.contains = EmptySchema() if contains is None else contains

    @classmethod
    def unmarshal(cls, schema):
        schema = deepcopy(schema)
        if schema.get('items') is not None:
            schema['items'] = {
                dict: lambda instance: Creator.create(instance.get('type')).unmarshal(instance),  # noqa: E501
                list: lambda instance: [Creator.create(element.get('type')).unmarshal(element) for element in instance],  # noqa: E501
            }[schema['items'].__class__](schema['items'])
        if schema.get('additionalItems') is not None:
            schema['additionalItems'] = (
                Creator.create(schema['additionalItems'].get('type'))
            ).unmarshal(schema['additionalItems'])
        if schema.get('contains') is not None:
            schema['contains'] = (
                Creator.create(schema['contains'].get('type'))
            ).unmarshal(schema['contains'])
        return super().unmarshal(schema)

    def accept(self, visitor, *args):
        return visitor.visit_array(self, *args)


class SchemaMap(Component, dict):

    @classmethod
    def unmarshal(cls, schema):
        return cls({
            name: Creator.create(member.get('type')).unmarshal(member)
            for name, member in schema.items()})


class Properties(SchemaMap):

    def accept(self, visitor, *args):
        return visitor.visit_properties(self, *args)


class Definitions(SchemaMap):

    def accept(self, visitor, *args):
        return visitor.visit_definitions(self, *args)


class Object(Primitive):

    def __init__(self, maxProperties=0, minProperties=0, required=None,
                 properties=None, patternProperties=None,
                 additionalProperties=None, dependencies=None,
                 propertyNames=None, **kwargs):
        super().__init__(**kwargs)
        self.maxProperties = maxProperties
        self.minProperties = minProperties
        self.required = [] if required is None else list(set(required))
        self.properties = Properties() if properties is None else properties
        self.patternProperties = patternProperties
        self.additionalProperties = EmptySchema() if additionalProperties is None else additionalProperties  # noqa: E501
        self.dependencies = dependencies
        self.propertyNames = EmptySchema() if properties is None else propertyNames  # noqa: E501

    @classmethod
    def unmarshal(cls, schema):
        schema = deepcopy(schema)
        schema['properties'] = Properties.unmarshal(schema.get('properties', {}))  # noqa: E501
        if schema.get('additionalProperties') is not None:
            schema['additionalProperties'] = (
                Creator.create(schema['additionalProperties'].get('type'))
            ).unmarshal(schema['additionalProperties'])
        return super().unmarshal(schema)

    def accept(self, visitor, *args):
        return visitor.visit_object(self, *args)


class Reference(Primitive):

    # https://tools.ietf.org/html/rfc3986#appendix-B
    expression = re.compile(r'^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?')  # noqa: E501

    def __init__(self, **kwargs):
        address = kwargs['$ref']
        if Reference.expression.match(address) is None:  # pragma: no cover
            raise ValueError('The value of the "$ref" property "%r" is not a valid URI Reference' % (address,))  # noqa: E501
        self.address = address
        self.resolved = False
        self.value = None
        super().__init__(**kwargs)

    def accept(self, visitor, *args):
        return visitor.visit_reference(self, *args)


class Union(Primitive):

    def accept(self, visitor, *args):
        return visitor.visit_union(self, *args)


class UnkownHandler:

    @classmethod
    def unmarshal(cls, schema):
        return Reference.unmarshal(schema) if '$ref' in schema else Enumeration.unmarshal(schema)  # noqa: E501
