from ..primitive import Array, Component, Object, Reference, Enumeration


class AvroSchemaVisitor:

    def visit_empty_schema(self, schema, *args):  # pragma: no cover
        return

    def visit_enumeration(self, enumeration, *args):
        return {
            'type': 'enum', 'name': enumeration.title,
            'symbols': enumeration.enum}

    def visit_boolean(self, boolean, *args):
        return {'type': 'boolean'}

    def visit_null(self, null, *args):
        return {'type': 'null'}

    def visit_number(self, number, *args):
        return {'type': 'double'}

    def visit_integer(self, integer, *args):
        return {'type': 'long'}

    def visit_string(self, string, *args):
        return {'type': 'string'}

    def visit_array(self, array, *args):
        if isinstance(array.items, Component):
            items = array.items.accept(self, *args)
        else:
            items = [element.accept(self, *args) for element in array.items][0]
        if 'fields' not in items:
            items = items['type']
        return {'type': 'array', 'items': items}

    def visit_object(self, obj, *args):
        fields = []
        for name, member in obj.properties.items():
            field = member.accept(self, *args)
            if isinstance(member, (Array, Object, Reference, Enumeration)):
                field = {'type': field}
            field.update({'name': name, 'doc': member.description})
            fields.append(field)
        for element in obj.allOf:
            fields.extend(element.accept(self, *args).get('fields', [element.accept(self, *args)]))  # noqa: E501
        return {'type': 'record', 'name': obj.title, 'fields': fields}

    def visit_reference(self, reference, *args):
        if reference.resolved:
            return reference.value.accept(self, *args)

    def visit_union(self, union, *args):
        return {'type': union.type}
