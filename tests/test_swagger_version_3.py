import json
import os
import unittest

from aptos.swagger.v3 import model
from aptos.swagger.v3.parser import OpenAPIParser

BASE_DIR = os.path.dirname(__file__)


class OpenAPIVersion3TestCase(unittest.TestCase):

    def runTest(self):
        with open(os.path.join(BASE_DIR, 'schema', 'petstore')) as fp:
            schema = json.load(fp)
        swagger = OpenAPIParser.parse(schema)
        self.assertIsInstance(swagger.paths['/pets']['get'].responses, model.Responses)  # noqa: E501
        self.assertTrue(swagger.components.schemas['Pets'].items.resolved)
        self.assertTrue(swagger.paths['/pets']['get'].responses['200'].content['application/json'].schema.resolved)  # noqa: E501
