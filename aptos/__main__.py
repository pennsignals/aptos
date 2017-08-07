import argparse
import json
import sys

from .parser import SchemaParser
from .visitor import ValidationVisitor
from .schema.visitor import AvroSchemaVisitor


def validate(arguments):
    with open(arguments.schema) as fp:
        schema = json.load(fp)
    component = SchemaParser.parse(schema)
    try:
        component.accept(ValidationVisitor(json.loads(arguments.instance)))
    except AssertionError as e:
        sys.exit('Error: {}'.format(e))


def convert(arguments):
    with open(arguments.schema) as fp:
        schema = json.load(fp)
    component = SchemaParser.parse(schema)
    Visitor = {
        'avro': AvroSchemaVisitor,
    }[arguments.format]
    print(json.dumps(component.accept(Visitor()), indent=2))


def main():
    parser = argparse.ArgumentParser(description='''
        aptos is a tool for validating client-submitted data using the
        JSON Schema vocabulary and converting JSON Schema documents to
        different data-interchange formats.
    ''', usage='%(prog)s [arguments] SCHEMA', epilog='''
        More information on JSON Schema: http://json-schema.org/''')
    subparsers = parser.add_subparsers(title='Arguments')

    validation = subparsers.add_parser('validate',
        help='Validate a JSON instance')
    validation.add_argument('-instance', type=str, default=json.dumps({}),
        help='JSON document being validated')
    validation.set_defaults(func=validate)

    conversion = subparsers.add_parser('convert',
        help='Convert a JSON Schema to a data-interchange format')
    conversion.add_argument('-format', type=str, choices=['avro'],
        help='data-interchange format')
    conversion.set_defaults(func=convert)

    parser.add_argument('schema', type=str,
        help='JSON document containing the description')

    arguments = parser.parse_args()
    arguments.func(arguments)


if __name__ == '__main__':
    main()
