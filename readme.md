<p align="center">
    <a href="https://github.com/pennsignals/aptos"><img src="https://rawgit.com/rightlag/d97e8d74d5bbb5b2e0cbe2938c40802d/raw/c957e9af39b1e6d94c1b5e823685084e7beba6ad/aptos.svg"></a>
</p>

<p align="center">
    <a href="https://travis-ci.org/pennsignals/aptos"><img src="https://img.shields.io/travis/pennsignals/aptos.svg?style=flat-square" alt="Build Status"></a>
    <a href="https://coveralls.io/github/pennsignals/aptos"><img src="https://img.shields.io/coveralls/pennsignals/aptos.svg?style=flat-square" alt="Coverage Status"></a>
</p>

---

`aptos` is a module that parses [JSON Schema](http://json-schema.org/) documents to validate client-submitted data and convert JSON schema documents to Avro schema documents.

## Usage

`aptos` supports validating client-submitted data and generates Avro structured messages from a given JSON Schema document.

```
usage: aptos [arguments] SCHEMA

aptos is a tool for validating client-submitted data using the JSON Schema
vocabulary and converting JSON Schema documents to different data-interchange
formats.

positional arguments:
  schema              JSON document containing the description

optional arguments:
  -h, --help          show this help message and exit

Arguments:
  {validate,convert}
    validate          Validate a JSON instance
    convert           Convert a JSON Schema to a different data-interchange
                      format

More information on JSON Schema: http://json-schema.org/

```

## Data Validation

Given a JSON Schema document, `aptos` can validate client-submitted data to require that it satisfies a certain number of criteria.

```json
{
    "title": "Product",
    "type": "object",
    "definitions": {
        "geographical": {
            "title": "Geographical",
            "description": "A geographical coordinate",
            "type": "object",
            "properties": {
                "latitude": { "type": "number" },
                "longitude": { "type": "number" }
            }
        }
    },
    "properties": {
        "id": {
            "description": "The unique identifier for a product",
            "type": "number"
        },
        "name": {
            "type": "string"
        },
        "price": {
            "type": "number",
            "minimum": 0,
            "exclusiveMinimum": true
        },
        "tags": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "minItems": 1,
            "uniqueItems": true
        },
        "dimensions": {
            "title": "Dimensions",
            "type": "object",
            "properties": {
                "length": {"type": "number"},
                "width": {"type": "number"},
                "height": {"type": "number"}
            },
            "required": ["length", "width", "height"]
        },
        "warehouseLocation": {
            "description": "Coordinates of the warehouse with the product",
            "$ref": "#/definitions/geographical"
        }
    },
    "required": ["id", "name", "price"]
}
```

Validation keywords such as `uniqueItems`, `required`, and `minItems` can be used in a schema to impose requirements for successful validation of an instance.

```python
import json

from aptos.parser import SchemaParser
from aptos.visitor import ValidationVisitor


with open('/path/to/schema') as fp:
    schema = json.load(fp)
component = SchemaParser.parse('/path/to/schema')
# Valid client-submitted data (instance)
instance = {
    "id": 2,
    "name": "An ice sculpture",
    "price": 12.50,
    "tags": ["cold", "ice"],
    "dimensions": {
        "length": 7.0,
        "width": 12.0,
        "height": 9.5
    },
    "warehouseLocation": {
        "latitude": -78.75,
        "longitude": 20.4
    }
}
component.accept(ValidationVisitor(instance))
```

## Structured Message Generation

Given a JSON Schema document, `aptos` can generate Avro structured messages.

### Avro

For brevity, the [Product](https://github.com/pennsignals/aptos/blob/master/tests/schema/product) schema is omitted from the example.

```python
import json

from aptos.parser import SchemaParser
from aptos.schema.visitor import AvroSchemaVisitor


with open('/path/to/schema') as fp:
    schema = json.load(fp)
component = SchemaParser.parse(schema)
record = component.accept(AvroSchemaVisitor())
print(json.dumps(record, indent=2))
```

The preceding code generates the following Avro schema:

```json
{
  "type": "record",
  "name": "Product",
  "fields": [
    {
      "type": "double",
      "name": "price",
      "doc": ""
    },
    {
      "type": "string",
      "name": "name",
      "doc": ""
    },
    {
      "type": {
        "type": "record",
        "name": "Geographical",
        "fields": [
          {
            "type": "double",
            "name": "latitude",
            "doc": ""
          },
          {
            "type": "double",
            "name": "longitude",
            "doc": ""
          }
        ]
      },
      "name": "warehouseLocation",
      "doc": "Coordinates of the warehouse with the product"
    },
    {
      "type": {
        "type": "record",
        "name": "Dimensions",
        "fields": [
          {
            "type": "double",
            "name": "height",
            "doc": ""
          },
          {
            "type": "double",
            "name": "length",
            "doc": ""
          },
          {
            "type": "double",
            "name": "width",
            "doc": ""
          }
        ]
      },
      "name": "dimensions",
      "doc": ""
    },
    {
      "type": {
        "type": "array",
        "items": "string"
      },
      "name": "tags",
      "doc": ""
    },
    {
      "type": "double",
      "name": "id",
      "doc": "The unique identifier for a product"
    }
  ]
}
```

## Maintainers

| ![Jason Walsh](https://avatars3.githubusercontent.com/u/2184329?v=3&s=128) |
|----------------------------------------------------------------------------|
| Jason Walsh [@rightlag](https://github.com/rightlag)                       |
