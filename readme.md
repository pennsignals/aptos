<p align="center">
    <a href="https://github.com/pennsignals/aptos"><img src="https://rawgit.com/rightlag/d97e8d74d5bbb5b2e0cbe2938c40802d/raw/c957e9af39b1e6d94c1b5e823685084e7beba6ad/aptos.svg"></a>
</p>

<p align="center">
    <a href="https://travis-ci.org/pennsignals/aptos"><img src="https://img.shields.io/travis/pennsignals/aptos.svg?style=flat-square" alt="Build Status"></a>
    <a href="https://coveralls.io/github/pennsignals/aptos"><img src="https://img.shields.io/coveralls/pennsignals/aptos.svg?style=flat-square" alt="Coverage Status"></a>
</p>

> Validate client-submitted data using [JSON Schema](http://json-schema.org/) documents and convert JSON Schema documents into different data-interchange formats.

## Contents

- [Installation](#installation)
- [Usage](#usage)
- [Data Validation](#data-validation)
- [Data Validation CLI](#data-validation-cli)
- [Data Validation API](#data-validation-api)
- [Structured Messaged Generation](#structured-message-generation)
- [Supported Data-Interchange Formats](#supported-data-interchange-formats)
- [Avro](#avro)
- [Data-Interchange CLI](#data-interchange-cli)
- [Data-Interchange API](#data-interchange-api)
- [Testing](#testing)
- [Additional Resources](#additional-resources)
- [Future Considerations](#future-considerations)
- [Maintainers](#maintainers)
- [Contributing](#contributing)

## Why aptos?

- Validate client-submitted data
- Convert JSON Schema documents into different data-interchange formats
- Simple syntax
- CLI support for data validation and JSON Schema conversion

## Installation

**via pip**

    $ pip install aptos

**via git**

    $ git clone https://github.com/pennsignals/aptos.git && cd aptos
    $ python setup.py install

## Usage

`aptos` supports the following capabilities:

 - **Data Validation:** Validate client-submitted data using [validation keywords](http://json-schema.org/latest/json-schema-validation.html#rfc.section.6) described in the JSON Schema specification.
 - **Schema Conversion:** Convert JSON Schema documents into different data-interchange formats. See the list of [supported data-interchange formats](#supported-data-interchange-formats) for more information.

```
usage: aptos [arguments] SCHEMA

aptos is a tool for validating client-submitted data using the JSON Schema
vocabulary and converts JSON Schema documents into different data-interchange
formats.

positional arguments:
  schema              JSON document containing the description

optional arguments:
  -h, --help          show this help message and exit

Arguments:
  {validate,convert}
    validate          Validate a JSON instance
    convert           Convert a JSON Schema into a different data-interchange
                      format

More information on JSON Schema: http://json-schema.org/

```

## Data Validation

Here is a basic example of a JSON Schema:

```json
{
    "title": "Person",
    "type": "object",
    "properties": {
        "firstName": {
            "type": "string"
        },
        "lastName": {
            "type": "string"
        },
        "age": {
            "description": "Age in years",
            "type": "integer",
            "minimum": 0
        }
    },
    "required": ["firstName", "lastName"]
}
```

Given a JSON Schema, `aptos` can validate client-submitted data to ensure that it satisfies a certain number of criteria.

JSON Schema [Validation keywords](http://json-schema.org/latest/json-schema-validation.html#rfc.section.6) such as `minimum` and `required` can be used to impose requirements for successful validation of an instance. In the JSON Schema above, both the `firstName` and `lastName` properties are required, and the `age` property *MUST* have a value greater than or equal to 0.

| Valid Instance :heavy_check_mark:                     | Invalid Instance :heavy_multiplication_x:                                                                               |
|-------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `{"firstName": "John", "lastName": "Doe", "age": 42}` | `{"firstName": "John", "age": -15}` (missing required property `lastName` and `age` is not greater than or equal to 0)  |

`aptos` can validate client-submitted data using either the CLI or the API:

### Data Validation CLI

    $ aptos validate -instance INSTANCE SCHEMA

**Arguments:**

 - **INSTANCE:** JSON document being validated
 - **SCHEMA:** JSON document containing the description

| Successful Validation :heavy_check_mark:                                                                 | Unsuccessful Validation :heavy_multiplication_x:                                                         |
|----------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| ![](https://user-images.githubusercontent.com/2184329/29053486-5c787966-7bbe-11e7-8fd3-4cb51d87d7d9.png) | ![](https://user-images.githubusercontent.com/2184329/29053538-afcce9c6-7bbe-11e7-8be5-61ac1d876fc1.png) |

### Data Validation API

```python
import json

from aptos.parser import SchemaParser
from aptos.visitor import ValidationVisitor


with open('/path/to/schema') as fp:
    schema = json.load(fp)
component = SchemaParser.parse(schema)
# Invalid client-submitted data (instance)
instance = {
  'firstName': 'John'
}
try:
    component.accept(ValidationVisitor(instance))
except AssertionError as e:
    print(e)  # instance {'firstName': 'John'} is missing required property 'lastName'
```

## Structured Message Generation

Given a JSON Schema, `aptos` can generate different structured messages.

:warning: **Note:** The JSON Schema being converted *MUST* be a valid [JSON Object](https://spacetelescope.github.io/understanding-json-schema/reference/object.html).

## Supported Data-Interchange Formats

| Format                                                              |         Supported        | Notes                       |
|---------------------------------------------------------------------|:------------------------:|-----------------------------|
| [Apache Avro](https://avro.apache.org/)                             |    :heavy_check_mark:    |                             |
| [Protocol Buffers](https://developers.google.com/protocol-buffers/) | :heavy_multiplication_x: | Planned for future releases |
| [Apache Thrift](https://thrift.apache.org/)                         | :heavy_multiplication_x: | Planned for future releases |
| [Apache Parquet](https://parquet.apache.org/)                       | :heavy_multiplication_x: | Planned for future releases |

### Avro

Using the `Person` schema in the previous example, `aptos` can convert the schema into the Avro data-interchange format using either the CLI or the API.

`aptos` maps the following JSON schema types to Avro types:

| JSON Schema Type | Avro Type |
|------------------|-----------|
| `string`         | `string`  |
| `boolean`        | `boolean` |
| `null`           | `null`    |
| `integer`        | `long`    |
| `number`         | `double`  |
| `object`         | `record`  |
| `array`          | `array`   |

> JSON Schema documents containing the `enum` validation keyword are mapped to Avro [`enum`](http://avro.apache.org/docs/current/spec.html#Enums) `symbols` attribute.

> JSON Schema documents with the `type` keyword as an array are mapped to Avro [Union](http://avro.apache.org/docs/current/spec.html#Unions) types.

## Data-Interchange CLI

    $ aptos convert -format FORMAT SCHEMA

**Arguments:**

 - **FORMAT:** Data-interchange format
 - **SCHEMA:** JSON document containing the description

<p align="center">
    <img src="https://user-images.githubusercontent.com/2184329/29071365-3d6e7504-7c11-11e7-959e-abcfe15f5e96.png" width="600">
</p>

## Data-Interchange API

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

The above code generates the following Avro schema:

```json
{
  "type": "record",
  "fields": [
    {
      "doc": "",
      "type": "string",
      "name": "lastName"
    },
    {
      "doc": "",
      "type": "string",
      "name": "firstName"
    },
    {
      "doc": "Age in years",
      "type": "long",
      "name": "age"
    }
  ],
  "name": "Person"
}
```

## Testing

All unit tests exist in the [tests](tests) directory.

To run tests, execute the following command:

    $ python setup.py test

## Additional Resources

 - [Stop Being a "Janitorial" Data Scientist](https://medium.com/@rightlag/stop-being-a-janitorial-data-scientist-5959cccbeac) - *A blog post explaining why aptos was created*
 - [Understanding JSON Schema](https://spacetelescope.github.io/understanding-json-schema/) - *An excellent guide for schema authors, from the [Space Telescope Science Institute](http://www.stsci.edu/portal/)*

## Future Considerations

- [Swagger](https://swagger.io/) support
- Additional [data-interchange](#supported-data-interchange-formats) formats

## Maintainers

| ![Jason Walsh](https://avatars3.githubusercontent.com/u/2184329?v=3&s=128) |
|:--------------------------------------------------------------------------:|
|                 [Jason Walsh](https://twitter.com/rightlag)                |

## Contributing

Contributions welcome! Please read the [`contributing.json`](contributing.json) file first.
