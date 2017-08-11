from ...primitive import Creator
from ...visitor import ResolveVisitor


class OpenAPIResolveVisitor(ResolveVisitor):

    def __init__(self, context):
        self.context = context

    def visit_reference(self, reference, *args):
        if reference.resolved:  # pragma: no cover
            return reference
        component, name = reference.address.split('/')[-2:]
        schema = self.context['components'][component][name]
        reference.value = Creator.create(schema.get('type')).unmarshal(schema)
        reference.value.accept(self, *args)
        reference.resolved = True
        return reference

    def visit_swagger(self, swagger, *args):
        swagger.paths.accept(self, *args)
        swagger.components.accept(self, *args)
        return swagger

    def visit_paths(self, paths, *args):
        for name, member in paths.items():
            paths[name] = member.accept(self, *args)

    def visit_parameters(self, parameters, *args):
        return parameters

    def visit_path_item(self, path_item, *args):
        path_item.parameters.accept(self, *args)
        for name, member in path_item.items():
            path_item[name] = member.accept(self, *args)
        return path_item

    def visit_responses(self, responses, *args):
        for name, member in responses.items():
            responses[name] = member.accept(self, *args)

    def visit_response(self, response, *args):
        response.content.accept(self, *args)
        return response

    def visit_content(self, content, *args):
        for name, member in content.items():
            content[name] = member.accept(self, *args)

    def visit_media_type(self, media_type, *args):
        media_type.schema.accept(self, *args)
        return media_type

    def visit_operation(self, operation, *args):
        operation.responses.accept(self, *args)
        return operation

    def visit_components(self, components, *args):
        components.schemas.accept(self, *args)
        return components

    def visit_schemas(self, schemas, *args):
        for name, member in schemas.items():
            schemas[name] = member.accept(self, *args)
