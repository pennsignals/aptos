import json
import os
import unittest

from aptos.swagger.v3 import model
from aptos.swagger.v3 import visitor

BASE_DIR = os.path.dirname(__file__)


class SwaggerVersion3TestCase(unittest.TestCase):

    def runTest(self):
        with open(os.path.join(BASE_DIR, 'schema', 'petstore')) as fp:
            schema = json.load(fp)
        swagger = model.Swagger.unmarshal(schema)
        self.assertIsInstance(swagger.paths['/pets']['get'].responses, model.Responses)  # noqa: E501
        swagger.accept(visitor.SpecificationResolveVisitor(schema))
        self.assertTrue(swagger.components.schemas['Pets'].items.resolved)
        self.assertTrue(swagger.paths['/pets']['get'].responses['200'].content['application/json'].schema.resolved)  # noqa: E501
