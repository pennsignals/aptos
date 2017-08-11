from copy import deepcopy

from ...primitive import Component, Creator, SchemaMap


class Swagger(Component):

    """This is the root document object of the
    `OpenAPI document <https://swagger.io/specification/#oasDocument>`_.
    """

    def __init__(self, openapi='3.0.0', info=None, servers=None, paths=None,
                 components=None, security=None, tags=None, externalDocs=None):
        self.openapi = openapi
        self.info = Info() if info is None else info
        self.servers = [] if servers is None else servers
        self.paths = Paths() if paths is None else paths
        self.components = Components() if components is None else components
        self.security = security
        self.tags = tags
        self.externalDocs = (
            ExternalDocumentation() if externalDocs is None else externalDocs)

    @classmethod
    def unmarshal(cls, schema):
        schema = deepcopy(schema)
        schema['info'] = Info.unmarshal(schema.get('info', {}))
        schema['paths'] = Paths.unmarshal(schema.get('paths', {}))
        schema['components'] = (
            Components.unmarshal(schema.get('components', {})))
        return cls(**schema)

    def accept(self, visitor, *args):
        return visitor.visit_swagger(self, *args)


class Components(Component):

    def __init__(self, schemas=None, responses=None, parameters=None,
                 examples=None, requestBodies=None, headers=None,
                 securitySchemes=None, links=None, callbacks=None):
        self.schemas = Schemas() if schemas is None else schemas
        self.responses = responses
        self.parameters = parameters
        self.examples = examples
        self.requestBodies = requestBodies
        self.headers = headers
        self.securitySchemes = securitySchemes
        self.links = links
        self.callbacks = callbacks

    @classmethod
    def unmarshal(cls, schema):
        schema['schemas'] = Schemas.unmarshal(schema.get('schemas', {}))
        return cls(**schema)

    def accept(self, visitor, *args):
        return visitor.visit_components(self, *args)


class Schemas(SchemaMap):

    def accept(self, visitor, *args):
        return visitor.visit_schemas(self, *args)


class Info(Component):

    def __init__(self, title='', description='', termsOfService='',
                 contact=None, license=None, version=''):
        self.title = title
        self.description = description
        self.termsOfService = termsOfService
        self.contact = Contact() if contact is None else contact
        self.license = License() if license is None else license
        self.version = version

    @classmethod
    def unmarshal(cls, schema):
        schema = deepcopy(schema)
        schema['contact'] = Contact(**schema.get('contact', {}))
        schema['license'] = License(**schema.get('license', {}))
        return cls(**schema)


class ExternalDocumentation(Component):

    def __init__(self, description='', url=''):
        self.description = description
        self.url = url


class Contact(Component):

    def __init__(self, name='', url='', email=''):
        self.name = name
        self.url = url
        self.email = email


class License(Component):

    def __init__(self, name='', url=''):
        self.name = name
        self.url = url


class Variables(Component, dict):

    @classmethod
    def unmarshal(cls, schema):
        return cls({
            name: ServerVariable(**member) for name, member in schema.items()})


class ServerVariable(Component):

    def __init__(self, enum=None, default='', description=''):
        self.enum = enum
        self.default = default
        self.description = description


class Server(Component):

    def __init__(self, url='', description='', variables=None):
        self.url = url
        self.description = description
        self.variables = Variables() if variables is None else variables

    @classmethod
    def unmarshal(cls, schema):
        schema = deepcopy(schema)
        schema['variables'] = Variables.unmarshal(schema.get('variables', {}))
        return cls(**schema)


class Response(Component):

    def __init__(self, description='', headers=None, content=None, links=None):
        self.description = description
        self.headers = headers
        self.content = Content() if content is None else content
        self.links = links

    @classmethod
    def unmarshal(cls, schema):
        if schema.get('content') is not None:
            schema['content'] = Content.unmarshal(schema['content'])
        return cls(**schema)

    def accept(self, visitor, *args):
        return visitor.visit_response(self, *args)


class Responses(Component, dict):

    @classmethod
    def unmarshal(cls, schema):
        return cls({
            name: Response.unmarshal(member)
            for name, member in schema.items()})

    def accept(self, visitor, *args):
        return visitor.visit_responses(self, *args)


class Operation(Component):

    def __init__(self, tags=None, summary='', description='',
                 externalDocs=None, operationId='', parameters=None,
                 requestBody=None, responses=None, callbacks=None,
                 deprecated=False, security=None, servers=None):
        self.tags = [] if tags is None else tags
        self.summary = summary
        self.description = description
        self.externalDocs = (
            ExternalDocumentation() if externalDocs is None else externalDocs)
        self.operationId = operationId
        self.parameters = Parameters() if parameters is None else parameters
        self.requestBody = (
            RequestBody() if requestBody is None else requestBody)
        self.responses = Responses() if responses is None else responses
        self.callbacks = callbacks
        self.deprecated = deprecated
        self.security = security

    @classmethod
    def unmarshal(cls, schema):
        schema = deepcopy(schema)
        schema['externalDocs'] = (
            ExternalDocumentation(**schema.get('externalDocs', {})))
        schema['parameters'] = (
            Parameters.unmarshal(schema.get('parameters', [])))
        if schema.get('requestBody') is not None:
            schema['requestBody'] = (
                RequestBody.unmarshal(schema['requestBody']))
        schema['responses'] = Responses.unmarshal(schema['responses'])
        return cls(**schema)

    def accept(self, visitor, *args):
        return visitor.visit_operation(self, *args)


class RequestBody(Component):

    def __init__(self, description='', content=None, required=False):
        self.description = description
        self.content = Content() if content is None else content
        self.required = required

    @classmethod
    def unmarshal(cls, schema):
        schema = deepcopy(schema)
        schema['content'] = Content.unmarshal(schema['content'])
        return cls(**schema)

    def accept(self, visitor, *args):
        return visitor.visit_request_body(self, *args)


class Content(Component, dict):

    @classmethod
    def unmarshal(cls, schema):
        return cls({
            name: MediaType.unmarshal(member)
            for name, member in schema.items()})

    def accept(self, visitor, *args):
        return visitor.visit_content(self, *args)


class MediaType(Component):

    def __init__(self, schema=None, example=None, examples=None,
                 encoding=None):
        self.schema = schema
        self.example = example
        self.examples = examples
        self.encoding = encoding

    @classmethod
    def unmarshal(cls, schema):
        schema = deepcopy(schema)
        if schema.get('schema') is not None:
            schema['schema'] = (
                Creator.create(schema.get('type'))
            ).unmarshal(schema['schema'])
        return cls(**schema)

    def accept(self, visitor, *args):
        return visitor.visit_media_type(self, *args)


class PathItem(Component, dict):

    def __init__(self, summary='', description='', servers=None,
                 parameters=None, **kwargs):
        super().__init__(**kwargs)
        self.reference = kwargs.get('reference', '')
        self.summary = summary
        self.description = description
        self.servers = [] if servers is None else servers
        self.parameters = Parameters() if parameters is None else parameters

    @classmethod
    def unmarshal(cls, schema):
        schema = deepcopy(schema)
        for operation in ('get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace'):  # noqa: E501
            if schema.get(operation) is not None:
                schema[operation] = Operation.unmarshal(schema[operation])
        return cls(**schema)

    def accept(self, visitor, *args):
        return visitor.visit_path_item(self, *args)


class Paths(Component, dict):

    @classmethod
    def unmarshal(cls, schema):
        return cls({
            name: PathItem.unmarshal(member)
            for name, member in schema.items()})

    def accept(self, visitor, *args):
        return visitor.visit_paths(self, *args)


class Parameters(Component, list):

    @classmethod
    def unmarshal(cls, schema):
        return cls(Parameter.unmarshal(element) for element in schema)

    def accept(self, visitor, *args):
        return visitor.visit_parameters(self, *args)


class Parameter(Component):

    def __init__(self, name='', description='', required=False,
                 deprecated=False, allowEmptyValue=False, style='',
                 explode=False, allowReserved=False, schema=None, example=None,
                 examples=None, **kwargs):
        # TODO: complete `Parameter` class
        parameterIn = kwargs.get('in', '')
        assert parameterIn in ('query', 'header', 'path', 'cookie')
        self.name = name
        self.parameterIn = parameterIn
        self.description = description
        self.required = required
        self.deprecated = deprecated
        self.allowEmptyValue = allowEmptyValue
        self.style = style
        self.explode = explode
        self.allowReserved = allowReserved
        self.schema = schema
        self.example = example
        self.examples = examples

    @classmethod
    def unmarshal(cls, schema):
        return cls(**schema)

    def accept(self, visitor, *args):
        return visitor.visit_parameter(self, *args)
