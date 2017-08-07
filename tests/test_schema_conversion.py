import json
import os
import unittest

from aptos.parser import SchemaParser
from aptos.schema.visitor import AvroSchemaVisitor

BASE_DIR = os.path.dirname(__file__)


class AvroSchemaTestCase(unittest.TestCase):

    def runTest(self):
        with open(os.path.join(BASE_DIR, 'schema', 'product')) as fp:
            schema = json.load(fp)
        component = SchemaParser.parse(schema)
        schema = component.accept(AvroSchemaVisitor())
        self.assertEqual(len(schema['fields']), 6)

        with open(os.path.join(BASE_DIR, 'schema', 'inventory')) as fp:
            schema = json.load(fp)
        component = SchemaParser.parse(schema)
        schema = component.accept(AvroSchemaVisitor())
        self.assertEqual(len(schema['fields']), 5)
