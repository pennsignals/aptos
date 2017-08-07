import re

from .primitive import Component, Creator, Translator


class SchemaArrayValidationHandler:

    def __init__(self, visitor):
        self.visitor = visitor

    def __call__(self, sequence, *args):
        errors = []
        for element in sequence:
            try:
                element.accept(self.visitor, *args)
            except AssertionError as e:
                errors.append(e.args[0])
                continue
        return errors


class ValidationVisitor:

    def __init__(self, instance):
        self.instance = instance

    def visit_empty_schema(self, schema, *args):  # pragma: no cover
        """Always passes validation."""
        return

    def visit_enumeration(self, enumeration, *args):
        self.visit_primitive(enumeration, *args)
        assert self.instance in enumeration.enum, 'instance %r is not equal to one of the elements %r' % (self.instance, enumeration)  # noqa: E501

    def visit_all_of(self, all_of, *args):
        for element in all_of:
            element.accept(self, *args)

    def visit_any_of(self, any_of, *args):
        if any_of:
            handler = SchemaArrayValidationHandler(self)
            errors = handler(any_of, *args)
            assert len(any_of) != len(errors), ', '.join(errors)

    def visit_one_of(self, one_of, *args):
        if one_of:
            handler = SchemaArrayValidationHandler(self)
            errors = handler(one_of, *args)
            assert len(errors) == 1, ', '.join(errors)

    def visit_primitive(self, primitive, *args):
        instance = self.instance
        if primitive.const is not None:
            assert instance == primitive.const, 'instance %r is not equal to %r' % (instance, primitive.const)  # noqa: E501
        if primitive.type is not None:
            assert {
                str: lambda instance: Translator.translate(instance).__name__.lower() == primitive.type,  # noqa: E501
                list: lambda instance: Translator.translate(instance).__name__.lower() in primitive.type,  # noqa: E501
            }[primitive.type.__class__](instance), 'instance %r is not in any of the sets listed %r' % (instance, primitive.type)  # noqa: E501
        primitive.allOf.accept(self, *args)
        primitive.anyOf.accept(self, *args)
        primitive.oneOf.accept(self, *args)

    def visit_boolean(self, boolean, *args):
        self.visit_primitive(boolean, *args)

    def visit_null(self, null, *args):
        self.visit_primitive(null, *args)

    def visit_numeric(self, numeric, *args):
        self.visit_primitive(numeric, *args)

        cls = args[0]
        instance = cls(self.instance)
        assert float(instance / numeric.multipleOf).is_integer(), 'instance %r division by %r is not an integer' % (instance, numeric.multipleOf)  # noqa: E501
        if numeric.maximum is not None:
            assert instance <= numeric.maximum, 'instance %r is not less than or exactly equal to %r' % (instance, numeric.maximum)  # noqa: E501
        if numeric.exclusiveMaximum is not None:
            assert instance < numeric.exclusiveMaximum, 'instance %r is not strictly less than (not equal to) %r' % (instance, numeric.exclusiveMaximum)  # noqa: E501
        if numeric.minimum is not None:
            assert instance >= numeric.minimum, 'instance %r is not greater than or exactly equal to %r' % (instance, numeric.minimum)  # noqa: E501
        if numeric.exclusiveMinimum is not None:
            assert instance > numeric.exclusiveMinimum, 'instance %r is not strictly greater than (not equal to) %r' % (instance, numeric.exclusiveMinimum)  # noqa: E501

    def visit_number(self, number, *args):
        self.visit_numeric(number, float)

    def visit_integer(self, integer, *args):
        self.visit_numeric(integer, int)

    def visit_string(self, string, *args):
        self.visit_primitive(string, *args)

        instance = self.instance
        if string.maxLength:
            assert len(instance) <= string.maxLength, 'instance %r is not less than, or equal to to %r' % (instance, string.maxLength)  # noqa: E501
        assert len(instance) >= string.minLength, 'instance %r is not greater than, or equal to %r' % (instance, string.minLength)  # noqa: E501
        if string.pattern:
            assert re.match(string.pattern, instance) is not None, 'instance %r does not match the regular expression %r' % (instance, string.pattern)  # noqa: E501

    def visit_array(self, array, *args):
        self.visit_primitive(array, *args)

        instance = self.instance
        items = [array.items] * len(instance) if isinstance(array.items, Component) else array.items  # noqa: E501
        for i, element in enumerate(instance):
            # Determine which subschemas apply to which elements of the array.
            try:
                items[i].accept(ValidationVisitor(element), *args)
            except IndexError:
                # If "items" is an array of schemas, validation succeeds if
                # every instance element at a position greater than the size of
                # "items" validates against "additionalItems".
                #
                # http://json-schema.org/latest/json-schema-validation.html#rfc.section.6.10
                array.additionalItems.accept(ValidationVisitor(element), *args)
        if array.maxItems:
            assert len(instance) <= array.maxItems, 'instance %r is not less than, or equal to %r' % (instance, array.maxItems)  # noqa: E501
        assert len(instance) >= array.minItems, 'instance %r is not greater than, or equal to %r' % (instance, array.minItems)  # noqa: E501
        if array.uniqueItems:
            assert len(set(instance)) == len(instance), 'instance %r contains duplicate elements' % (instance,)  # noqa: E501
        # TODO: contains
        array.contains.accept(self, *args)

    def visit_properties(self, properties, *args):
        instance = self.instance
        additionalProperties = args[0]
        for name, member in instance.items():
            # Validation succeeds if, for each name that appears in both the
            # instance and as a name within this keyword's value.
            try:
                properties[name].accept(ValidationVisitor(member), *args)
            except KeyError:
                # Validation with "additionalProperties" applies only to the
                # child values of instance names that do not match any names in
                # "properties", and do not match any regular expression in
                # "patternProperties".
                #
                # http://json-schema.org/latest/json-schema-validation.html#rfc.section.6.20
                additionalProperties.accept(ValidationVisitor(member), *args)

    def visit_definitions(self, definitions, *args):  # pragma: no cover
        """This keyword plays no role in validation per se. Its role is to
        provide a standardized location for schema authors to inline JSON
        Schemas into a more general schema.

        http://json-schema.org/latest/json-schema-validation.html#rfc.section.7.1
        """
        return

    def visit_object(self, obj, *args):
        self.visit_primitive(obj, *args)

        instance = self.instance
        if obj.maxProperties:
            assert len(instance) <= obj.maxProperties, 'instance %r number of properties is not less than, or equal to %r' % (instance, obj.maxProperties)  # noqa: E501
        assert len(instance) >= obj.minProperties, 'instance %r number of properties is not greater than, or equal to %r' % (instance, obj.minProperties)  # noqa: E501
        for element in obj.required:
            assert element in instance, 'instance %r is missing required property %r' % (instance, element)  # noqa: E501
        obj.properties.accept(self, obj.additionalProperties)

    def visit_reference(self, reference, *args):
        if reference.resolved:  # pragma: no cover
            reference.value.accept(self.instance, *args)

    def visit_union(self, union, *args):
        self.visit_primitive(union, *args)


class ResolveVisitor:

    def __init__(self, context):
        self.context = context

    def visit_empty_schema(self, schema, *args):  # pragma: no cover
        return

    def visit_enumeration(self, enumeration, *args):
        return self.visit_primitive(enumeration, *args)

    def visit_all_of(self, all_of, *args):
        for i, element in enumerate(all_of):
            # Resolve each member recursively.
            element = self.visit_primitive(element, *args)
            all_of[i] = element.accept(self, *args)

    def visit_any_of(self, any_of, *args):
        for i, element in enumerate(any_of):
            # Resolve each member recursively.
            element = self.visit_primitive(element, *args)
            any_of[i] = element.accept(self, *args)

    def visit_one_of(self, one_of, *args):
        for i, element in enumerate(one_of):
            # Resolve each member recursively.
            element = self.visit_primitive(element, *args)
            one_of[i] = element.accept(self, *args)

    def visit_primitive(self, primitive, *args):
        primitive.allOf.accept(self, *args)
        primitive.anyOf.accept(self, *args)
        primitive.oneOf.accept(self, *args)
        primitive.definitions.accept(self, *args)
        return primitive

    def visit_boolean(self, boolean, *args):
        return self.visit_primitive(boolean, *args)

    def visit_null(self, null, *args):
        return self.visit_primitive(null, *args)

    def visit_number(self, number, *args):
        return self.visit_primitive(number, *args)

    def visit_integer(self, integer, *args):
        return self.visit_primitive(integer, *args)

    def visit_string(self, string, *args):
        return self.visit_primitive(string, *args)

    def visit_array(self, array, *args):
        array = self.visit_primitive(array, *args)
        if isinstance(array.items, Component):
            array.items = array.items.accept(self, *args)
        else:
            array.items = [element.accept(self, *args) for element in array.items]  # noqa: E501
        array.additionalItems = array.additionalItems.accept(self, *args)
        array.contains = array.contains.accept(self, *args)
        return array

    def visit_properties(self, properties, *args):
        for name, member in properties.items():
            # Resolve each member recursively.
            member = self.visit_primitive(member, *args)
            properties[name] = member.accept(self, *args)

    def visit_definitions(self, definitions, *args):
        for name, member in definitions.items():
            # Resolve each member recursively.
            member = self.visit_primitive(member, *args)
            definitions[name] = member.accept(self, *args)

    def visit_object(self, obj, *args):
        obj = self.visit_primitive(obj, *args)
        obj.properties.accept(self, *args)
        return obj

    def visit_reference(self, reference, *args):
        if reference.resolved:  # pragma: no cover
            return reference
        definition = reference.address.split('/')[-1]
        schema = self.context['definitions'][definition]
        reference.value = Creator.create(schema.get('type')).unmarshal(schema)
        # Resolve the value returned from the Creator.
        self.visit_primitive(reference.value, *args)
        reference.resolved = True
        return reference

    def visit_union(self, union, *args):
        return self.visit_primitive(union, *args)
