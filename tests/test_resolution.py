import json
import os
import unittest

from aptos.primitive import Object, Primitive
from aptos.visitor import ResolveVisitor

BASE_DIR = os.path.dirname(__file__)


class ResolutionTestCase(unittest.TestCase):

    def runTest(self):
        with open(os.path.join(BASE_DIR, 'schema', 'product')) as fp:
            schema = json.load(fp)
        component = Object.unmarshal(schema)
        component.accept(ResolveVisitor(schema))
        self.assertTrue(component.properties['warehouseLocation'].resolved)
        self.assertIsInstance(
            component.properties['warehouseLocation'].value, Object)

        with open(os.path.join(BASE_DIR, 'schema', 'address')) as fp:
            schema = json.load(fp)
        component = Primitive.unmarshal(schema)
        component.accept(ResolveVisitor(schema))
        self.assertTrue(component.allOf[0].resolved)

        with open(os.path.join(BASE_DIR, 'schema', 'avro')) as fp:
            schema = json.load(fp)
        component = Primitive.unmarshal(schema)
        component.accept(ResolveVisitor(schema))
        self.assertTrue(component.oneOf[0].resolved)

        with open(os.path.join(BASE_DIR, 'schema', 'inventory')) as fp:
            schema = json.load(fp)
        component = Object.unmarshal(schema)
        component.accept(ResolveVisitor(schema))
        for member in component.properties['units'].items:
            self.assertTrue(member.resolved)
