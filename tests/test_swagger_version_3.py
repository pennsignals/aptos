import json
import os
import unittest

from aptos import primitive
from aptos.swagger.v3 import model
from aptos.swagger.v3.parser import OpenAPIParser

BASE_DIR = os.path.dirname(__file__)


class OpenAPIVersion3TestCase(unittest.TestCase):

    def runTest(self):
        with open(os.path.join(BASE_DIR, 'schema', 'swagger', 'petstore')) as fp:  # noqa: E501
            schema = json.load(fp)
        swagger = OpenAPIParser.parse(schema)

        parameters = swagger.paths['/pets']['get'].parameters
        self.assertIsInstance(parameters[0].schema, primitive.Array)
        self.assertIsInstance(parameters[0].schema.items, primitive.String)
        self.assertIsInstance(parameters[1].schema, primitive.Integer)

        content = swagger.paths['/pets']['get'].responses['200'].content['application/json']  # noqa: E501
        self.assertTrue(content.schema.items.resolved)
        self.assertTrue(swagger.components.schemas['Pet'].allOf[0].resolved)

        with open(os.path.join(BASE_DIR, 'schema', 'swagger', 'uber')) as fp:
            schema = json.load(fp)
        swagger = OpenAPIParser.parse(schema)

        content = swagger.paths['/products']['get'].responses['200'].content['application/json']  # noqa: E501
        self.assertTrue(content.schema.resolved)
        self.assertEqual(swagger.servers[0].url, 'https://api.uber.com/v1')

        with open(os.path.join(BASE_DIR, 'schema', 'swagger', 'links')) as fp:
            schema = json.load(fp)
        swagger = OpenAPIParser.parse(schema)

        link = swagger.paths['/2.0/users/{username}']['get'].responses['200'].links['userRepositories']  # noqa: E501
        self.assertTrue(link.resolved)
        self.assertIsInstance(link.value, model.Link)

        with open(os.path.join(BASE_DIR, 'schema', 'swagger', 'examples')) as fp:  # noqa:E501
            schema = json.load(fp)
        swagger = OpenAPIParser.parse(schema)

        examples = swagger.paths['/']['get'].responses['200'].content['application/json'].examples  # noqa: E501
        self.assertIsInstance(examples, model.Examples)
        self.assertIsInstance(examples['foo'], model.Example)
