from . import model
from ...primitive import Creator
from ...visitor import ResolveVisitor


class OpenAPIResolveVisitor(ResolveVisitor):

    components = {
        'responses': model.Response,
        'parameters': model.Parameter,
        'examples': model.Example,
        'requestBodies': model.RequestBody,
        'headers': model.Header,
        'securitySchemes': model.SecurityScheme,
        'links': model.Link,
        'callbacks': model.Callback,
    }

    def __init__(self, context):
        self.context = context

    def visit_reference(self, reference, *args):
        if reference.resolved:  # pragma: no cover
            return reference
        # A set of reusable objects for different aspects of the OAS.
        component, name = reference.address.split('/')[-2:]
        schema = self.context['components'][component][name]
        # Class is either an in-line or referenced schema.
        reference.value = OpenAPIResolveVisitor.components.get(
            component,
            Creator.create(schema.get('type'))
        ).unmarshal(schema)
        reference.value.accept(self, *args)
        reference.resolved = True
        return reference

    def visit_servers(self, servers, *args):
        for i, server in enumerate(servers):
            for name, variable in server.variables.items():
                # Variable substitutions will be made when a variable is named
                # in {brackets}.
                servers[i].url = (
                    servers[i].url.format(**{name: variable.default})
                )

    def visit_specification(self, specification, *args):
        specification.servers.accept(self, *args)
        specification.paths.accept(self, *args)
        specification.components.accept(self, *args)
        return specification

    def visit_components(self, components, *args):
        components.schemas.accept(self, *args)
        components.responses.accept(self, *args)
        components.parameters.accept(self, *args)
        components.requestBodies.accept(self, *args)
        components.headers.accept(self, *args)
        components.callbacks.accept(self, *args)
        return components

    def visit_paths(self, paths, *args):
        for name, member in paths.items():
            paths[name] = member.accept(self, *args)

    def visit_parameters(self, parameters, *args):
        for i, element in enumerate(parameters):
            parameters[i] = element.accept(self, *args)

    def visit_component_parameters(self, component_parameters, *args):
        for name, member in component_parameters.items():
            component_parameters[name] = member.accept(self, *args)

    def visit_parameter(self, parameter, *args):
        parameter.schema = parameter.schema.accept(self, *args)
        parameter.content = parameter.content.accept(self, *args)
        return parameter

    def visit_path_item(self, path_item, *args):
        path_item.servers.accept(self, *args)
        path_item.parameters.accept(self, *args)
        for name, member in path_item.items():
            path_item[name] = member.accept(self, *args)
        return path_item

    def visit_responses(self, responses, *args):
        for name, member in responses.items():
            # A Reference Object can link to a response that the OpenAPI
            # Object's components/responses section defines.
            responses[name] = member.accept(self, *args)

    def visit_response(self, response, *args):
        response.headers.accept(self, *args)
        response.content.accept(self, *args)
        response.links.accept(self, *args)
        return response

    def visit_content(self, content, *args):
        for name, member in content.items():
            content[name] = member.accept(self, *args)

    def visit_media_type(self, media_type, *args):
        media_type.schema.accept(self, *args)
        media_type.encoding.accept(self, *args)
        return media_type

    def visit_encoding(self, encoding, *args):
        encoding.headers.accept(self, *args)
        return encoding

    def visit_operation(self, operation, *args):
        operation.parameters.accept(self, *args)
        operation.requestBody = operation.requestBody.accept(self, *args)
        operation.responses.accept(self, *args)
        operation.callbacks.accept(self, *args)
        operation.servers.accept(self, *args)
        return operation

    def visit_request_bodies(self, request_bodies, *args):
        for name, member in request_bodies.items():
            request_bodies[name] = member.accept(self, *args)

    def visit_request_body(self, request_body, *args):
        request_body.content.accept(self, *args)
        return request_body

    def visit_headers(self, headers, *args):
        for name, member in headers.items():
            headers[name] = member.accept(self, *args)

    def visit_header(self, header, *args):
        header.schema = header.schema.accept(self, *args)
        header.content = header.content.accept(self, *args)
        return header

    def visit_callbacks(self, callbacks, *args):
        for name, member in callbacks.items():
            callbacks[name] = member.accept(self, *args)

    def visit_callback(self, callback, *args):
        for name, member in callback.items():
            callback[name] = member.accept(self, *args)
        return callback

    def visit_schemas(self, schemas, *args):
        for name, member in schemas.items():
            schemas[name] = member.accept(self, *args)

    def visit_links(self, links, *args):
        for name, member in links.items():
            links[name] = member.accept(self, *args)

    def visit_link(self, link, *args):
        return link

    def visit_security_schemes(self, security_schemes, *args):
        for name, member in security_schemes.items():
            security_schemes[name] = member.accept(self, *args)
