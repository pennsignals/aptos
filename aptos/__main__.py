import argparse
import json

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
        print('Error: {}'.format(e))


def convert(arguments):
    with open(arguments.schema) as fp:
        schema = json.load(fp)
    component = SchemaParser.parse(schema)
    Visitor = {
        'avro': AvroSchemaVisitor,
    }[arguments.format]
    print(json.dumps(component.accept(Visitor()), indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-schema', type=str, required=True)
    subparsers = parser.add_subparsers()

    validation = subparsers.add_parser('validate')
    validation.add_argument('-instance', type=str, default=json.dumps({}))
    validation.set_defaults(func=validate)

    conversion = subparsers.add_parser('convert')
    conversion.add_argument('-format', type=str)
    conversion.set_defaults(func=convert)

    arguments = parser.parse_args()
    arguments.func(arguments)


if __name__ == '__main__':
    main()
