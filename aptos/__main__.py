import argparse
import json
import sys

from .parser import SchemaParser
from .primitive import Object
from .visitor import ValidationVisitor
from .schema.visitor import AvroSchemaVisitor


class TermColors:

    GREEN = '\033[92m'
    RED = '\033[91m'
    DEFAULT = '\033[0m'


def validate(arguments):
    with open(arguments.schema) as fp:
        schema = json.load(fp)
    component = SchemaParser.parse(schema)
    instance = json.loads(arguments.instance)
    try:
        component.accept(ValidationVisitor(instance))
    except AssertionError as e:
        sys.exit('{}error{} {!r}'.format(
            TermColors.RED, TermColors.DEFAULT, e.args[0]))
    print('{}success{} instance {!r} is valid against the schema {!r}'.format(
        TermColors.GREEN, TermColors.DEFAULT, instance, arguments.schema))


def convert(arguments):
    with open(arguments.schema) as fp:
        schema = json.load(fp)
    component = SchemaParser.parse(schema)
    if not isinstance(component, Object):
        sys.exit('{}error{} cannot convert schema {!r} into {!r} format, schema must be of type "object"'.format(TermColors.RED, TermColors.DEFAULT, arguments.schema, arguments.format))  # noqa: E501
    Visitor = {
        'avro': AvroSchemaVisitor,
    }[arguments.format]
    print(json.dumps(component.accept(Visitor()), indent=2))


def main():
    parser = argparse.ArgumentParser(description='''
        aptos is a tool for validating client-submitted data using the
        JSON Schema vocabulary and converts JSON Schema documents into
        different data-interchange formats.
    ''', usage='%(prog)s [arguments] SCHEMA', epilog='''
        More information on JSON Schema: http://json-schema.org/''')
    subparsers = parser.add_subparsers(title='Arguments')

    validation = subparsers.add_parser(
        'validate', help='Validate a JSON instance')
    validation.add_argument(
        '-instance', type=str, default=json.dumps({}),
        help='JSON document being validated')
    validation.set_defaults(func=validate)

    conversion = subparsers.add_parser(
        'convert', help='''
        Convert a JSON Schema into a different data-interchange format''')
    conversion.add_argument(
        '-format', type=str, choices=['avro'], help='data-interchange format')
    conversion.set_defaults(func=convert)

    parser.add_argument(
        'schema', type=str, help='JSON document containing the description')

    arguments = parser.parse_args()
    arguments.func(arguments)


if __name__ == '__main__':
    main()
