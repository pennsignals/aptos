import json
import unittest

from aptos import primitive
from aptos.visitor import ValidationVisitor


class StringTestCase(unittest.TestCase):

    def runTest(self):
        schema = json.loads('''
            {
                "type": "string",
                "maxLength": 3
            }
        ''')
        string = primitive.String.unmarshal(schema)
        with self.assertRaises(AssertionError):
            string.accept(ValidationVisitor('A green door'))

        schema = json.loads('''
            {
                "type": "string",
                "minLength": 15
            }
        ''')
        string = primitive.String.unmarshal(schema)
        with self.assertRaises(AssertionError):
            string.accept(ValidationVisitor('A green door'))

        schema = json.loads(r'''
            {
                "type": "string",
                "pattern": "gray|grey"
            }
        ''')
        string = primitive.String.unmarshal(schema)
        with self.assertRaises(AssertionError):
            string.accept(ValidationVisitor('green'))


class BooleanTestCase(unittest.TestCase):

    def runTest(self):
        schema = json.loads('''
            {
                "type": "boolean"
            }
        ''')
        boolean = primitive.Boolean.unmarshal(schema)
        with self.assertRaises(AssertionError):
            boolean.accept(ValidationVisitor('true'))


class NullTestCase(unittest.TestCase):

    def runTest(self):
        schema = json.loads('''
            {
                "type": "null"
            }
        ''')
        null = primitive.Null.unmarshal(schema)
        with self.assertRaises(AssertionError):
            null.accept(ValidationVisitor(False))


class ArrayTestCase(unittest.TestCase):

    def runTest(self):
        schema = json.loads('''
            {
                "type": "array",
                "items": [
                    {
                        "type": "string"
                    }
                ],
                "minItems": 1,
                "uniqueItems": true
            }
        ''')
        array = primitive.Array.unmarshal(schema)
        with self.assertRaises(AssertionError):
            array.accept(ValidationVisitor([]))

        with self.assertRaises(AssertionError):
            array.accept(ValidationVisitor(['home', 'home', 'green']))

        schema = json.loads('''
            {
                "type": "array",
                "items": [
                    {
                        "type": "string"
                    }
                ],
                "additionalItems": {
                    "type": "number"
                },
                "minItems": 1,
                "uniqueItems": true
            }
        ''')
        array = primitive.Array.unmarshal(schema)
        with self.assertRaises(AssertionError):
            array.accept(ValidationVisitor(['home', 'string']))

        schema = json.loads('''
            {
                "type": "array",
                "maxItems": 1
            }
        ''')
        array = primitive.Array.unmarshal(schema)
        with self.assertRaises(AssertionError):
            array.accept(ValidationVisitor([1, 2, 3]))


class NumericTestCase(unittest.TestCase):

    def runTest(self):

        schema = json.loads('''
            {
                "type": "number",
                "minimum": 0,
                "exclusiveMaximum": 100
            }
        ''')
        number = primitive.Number.unmarshal(schema)
        with self.assertRaises(AssertionError):
            number.accept(ValidationVisitor(100.0))

        with self.assertRaises(AssertionError):
            number.accept(ValidationVisitor(-1.0))

        schema = json.loads('''
            {
                "type": "number",
                "multipleOf": -1
            }
        ''')
        with self.assertRaises(ValueError):
            # The value of "multipleOf" MUST be a number, strictly greater
            # than 0.
            primitive.Number.unmarshal(schema)

        schema = json.loads('''
            {
                "type": "number",
                "exclusiveMinimum": 50
            }
        ''')
        number = primitive.Number.unmarshal(schema)
        with self.assertRaises(AssertionError):
            number.accept(ValidationVisitor(20.0))

        schema = json.loads('''
            {
                "type": "number",
                "maximum": 100
            }
        ''')
        number = primitive.Number.unmarshal(schema)
        with self.assertRaises(AssertionError):
            number.accept(ValidationVisitor(101.0))

        schema = json.loads('''
            {
                "type": "integer"
            }
        ''')
        integer = primitive.Integer.unmarshal(schema)
        with self.assertRaises(AssertionError):
            integer.accept(ValidationVisitor(3.14159265359))


class ObjectTestCase(unittest.TestCase):

    def runTest(self):
        schema = json.loads('''
            {
                "type": "object",
                "properties": {
                    "firstName": {
                        "type": "string"
                    },
                    "lastName": {
                        "type": "string"
                    },
                    "age": {
                        "type": "integer",
                        "minimum": 0
                    }
                },
                "required": ["firstName", "lastName"]
            }
        ''')
        obj = primitive.Object.unmarshal(schema)
        with self.assertRaises(AssertionError):
            # Missing required properties "firstName" and "lastName".
            obj.accept(ValidationVisitor({'age': -1}))

        with self.assertRaises(AssertionError):
            # "age" is not greater than or exactly equal to 0.
            obj.accept(ValidationVisitor({
                'firstName': 'John', 'lastName': 'Doe', 'age': -1}))

        schema = json.loads('''
            {
                "type": "object",
                "properties": {
                    "firstName": {
                        "type": "string"
                    },
                    "lastName": {
                        "type": "string"
                    }
                },
                "additionalProperties": {
                    "type": "string"
                }
            }
        ''')
        obj = primitive.Object.unmarshal(schema)
        with self.assertRaises(AssertionError):
            # "id" is not of type "string." "additionalProperties" MUST be of
            # type "string."
            obj.accept(ValidationVisitor({
                'firstName': 'John', 'lastName': 'Doe', 'age': 40, 'id': 1}))

        schema = json.loads('''
            {
                "type": "object",
                "maxProperties": 1
            }
        ''')
        obj = primitive.Object.unmarshal(schema)
        with self.assertRaises(AssertionError):
            # "properties" is not less than, or equal to 1.
            obj.accept(ValidationVisitor({
                'firstName': 'John', 'lastName': 'Doe'}))


class ConstantTestCase(unittest.TestCase):

    def runTest(self):

        schema = json.loads('''
            {
                "type": "object",
                "properties": {
                    "five": {
                        "type": "number",
                        "const": 5.0
                    }
                }
            }
        ''')
        obj = primitive.Object.unmarshal(schema)
        with self.assertRaises(AssertionError):
            obj.accept(ValidationVisitor({'five': 0.0}))


class AllOfTestCase(unittest.TestCase):

    def runTest(self):
        schema = json.loads('''
            {
                "allOf": [
                    {
                        "type": "string",
                        "maxLength": 3
                    }
                ]
            }
        ''')
        component = primitive.Primitive.unmarshal(schema)
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor('green'))


class AnyOfTestCase(unittest.TestCase):

    def runTest(self):
        schema = json.loads('''
            {
                "anyOf": [
                    {
                        "type": "string",
                        "maxLength": 5
                    },
                    {
                        "type": "number",
                        "minimum": 0
                    }
                ]
            }
        ''')
        component = primitive.Primitive.unmarshal(schema)
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor('A green door'))

        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor(-5.0))


class OneOfTestCase(unittest.TestCase):

    def runTest(self):
        schema = json.loads('''
            {
                "oneOf": [
                    {
                        "type": "number",
                        "multipleOf": 5
                    },
                    {
                        "type": "number",
                        "multipleOf": 3
                    }
                ]
            }
        ''')
        component = primitive.Primitive.unmarshal(schema)
        with self.assertRaises(AssertionError):
            component.accept(ValidationVisitor(2.0))


class MultipleTypeTestCase(unittest.TestCase):

    def runTest(self):
        schema = json.loads('''
            {
                "type": ["number", "string"]
            }
        ''')
        union = primitive.Union.unmarshal(schema)
        with self.assertRaises(AssertionError):
            # "boolean" is not in any of the sets listed "number", or "string."
            union.accept(ValidationVisitor(True))


class EnumerationTestCase(unittest.TestCase):

    def runTest(self):
        schema = json.loads('''
            {
                "enum": ["red", "amber", "green"]
            }
        ''')
        enumeration = primitive.Enumeration.unmarshal(schema)
        with self.assertRaises(AssertionError):
            enumeration.accept(ValidationVisitor('blue'))
