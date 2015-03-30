# values

There are currently two types of value for options numeric and set. In the example above ```"colour"``` is a set and ```"wheels"``` is a numeric. Both of these types can be written to include additional information and have sub-types. 

Currently there are six types you can use:

+ **set:string**
+ **set:resource**
+ **numeric::number**
+ **numeric::set**
+ **numeric::range**
+ **numeric::step**

The only required attribute for a value is "type".

All values can be written as a json object in this way but there are also shorthand ways of expressing certain types, see below.

## set values

Set value types are used to express discrete optional variation in a product attribute. There are two set types, string and resource. String values are used to express any arbitrary values types, and resource types refer to other winnow resource documents by path.

# set::string

+ **type** - The type of value, One of the six types below  *(required)*
+ **name** - A display name  *(optional)*
+ **scopes** - A list of scopes that limit the visibility of this value in the winnow pipeline *(optional)*
+ **description** - A short description  *(optional)*
+ **image_uri** - A reference to an image used to represent this range. Given as an object with a single key "asset" and a value giving a path relative to the location of this document. *(optional)*
+ **values** - A list of string values objects  *(required)*
+ **default** - The value in the default value object  *(optional)*

Sets of strings are the most common value type are can be used to express any kind of choice or collection of values. They are very flexible and can be written in a variety of ways:

The full long version:

```json
{
    "colour": {
        "type": set::string,
        "name": u"colour",
        "description": "Please choose one of the colours",
        "default": "red",
        "values": [
            {
                "type": "string",
                "name": u"Red",
                "description": u"the colour red",
                "image_uri": u"http://something.com/khgfdkyg.png",
                "value": u"red",
            },
            {
                u"type": "string",
                u"name": u"Blue",
                u"description": u"the colour blue",
                u"image_uri": u"http://something.com/khgfdkyg.png",
                u"value": u"blue"
            }
        ]
    }
}
```

You can use shorthand syntax for just the values:

 ```json
{
    "colour": {
        "type": set::string,
        "name": u"colour",
        "description": "Please choose one of the colours",
        "default": "red",
        "values": ["red", "blue"]
    }
}
```

Or more concisely still if you use shorthand syntax for the whole object:

 ```json
{
    "colour": ["red", "blue"]
}
```

or for a single value even:

```json
{
    "colour": "red"
}
```

String values can also be extended with extra attributes to express choices between more complex data types. In this example numeric data is used inside a size object. Putting numeric data inside a set::string value allows you to compose complex data types and add additional data to each value, such as description, but the "value" key in the string object is all the is used in winnow operations so numeric values are not used for comparison. To do this you have to use the full long syntax:


```json
{
    "size":{
        "type": "set::string",
        "name": "sizes",
        "description": "available sheet sizes",
        "values": [
            {
                "type": "string",
                "name": "1200x2400",
                "description": "1200mm x 2400mm",
                "value": "1200x2400",
                "size":{
                    "units": "mm",
                    "width": 1200,
                    "heights": 2400
                }
            },
                  {
                "type": "string",
                "name": "1220x2440",
                "description": "1220mm x 2440mm",
                "value": "1220x2440",
                "size":{
                    "units": "mm",
                    "width": 1220,
                    "heights": 2440
                }
            }
        ]
    }
}
```

set::string can also contain nested options sets. The parent of a nested option has to use the longer syntax in order to have somewhere to put the child options. 

```json
"colour": {
    "type": set::string,
    "name": u"colour",
    "description": "Please choose one of the colours",
    "default": "red",
    "values": [
        {
            "type": "string",
            "name": u"Red",
            "description": u"the colour red",
            "image_uri": u"http://something.com/khgfdkyg.png",
            "value": u"red",
            "options":{
                type": set::string,
                "name": u"varnish",
                "description": "Please choose varnish type",
                "default": "matt",
                "values":[
                    {
                    "type": "string",
                    "name": u"Matt",
                    "description": u"Use matt varish",
                    "image_uri": u"http://something.com/khgfdkyg.png",
                    "value": u"matt",
                    },
                    {
                    "type": "string",
                    "name": u"Gloss",
                    "description": u"Use gloww varish",
                    "image_uri": u"http://something.com/khgfdkyg.png",
                    "value": u"gloss",
                    }
                ]
            }
        },
        {
            u"type": "string",
            u"name": u"Blue",
            u"description": u"the colour blue",
            u"image_uri": u"http://something.com/khgfdkyg.png",
            u"value": u"blue"
        }
    ]
}
```

# set::resource

Sets for resources are much like sets of strings except their "value" is always the path of another winnow document.

+ **type** - The type of value, One of the six types below  *(required)*
+ **name** - A display name  *(optional)*
+ **scopes** - A list of scopes that limit the visibility of this value in the winnow pipeline *(optional)*
+ **description** - A short description  *(optional)*
+ **image_uri** - A reference to an image used to represent this range. Given as an object with a single key "asset" and a value giving a path relative to the location of this document. *(optional)*
+ **values** - A list of string values objects  *(required)*
+ **default** - The value in the default value object  *(optional)*


A set::resource is always written like this and doesn't have a shorthand version:

```json
{
    "material": {
        "type": "set::resource",
        "name": "Material",
        "description": "Choose one of the materials",
        "values": [
            "/materials/opendesk/sheets/wood/composite/plywood",
            "/materials/opendesk/sheets/wood/composite/plywood/pre-laminated-plywood/wisa-multiwall"
        ]
    }
}
```

Only ```type``` and ```values``` are required.

You can ask winnow to inline the referenced resources if you want to and the resource documents will be written inline in place of their links. This works because all winnow documents with ```path``` attributes are themselves value types.

## numeric values

Numeric value types can be used to express possible variation of a number and all four numeric value types can be used interchangeably and compared to each other.

# numeric::number - A single number

+ **type** - The type of value, One of the six types below  *(required)*
+ **name** - A display name  *(optional)*
+ **scopes** - A list of scopes that limit the visibility of this value in the winnow pipeline *(optional)*
+ **description** - A short description  *(optional)*
+ **image_uri** - A reference to an image used to represent this range. Given as an object with a single key "asset" and a value giving a path relative to the location of this document. *(optional)*
+ **value** - A single number  *(required)*

example:

 ```json
 {
    "size" : {
        "type": "numeric::number",
        "name": "Size",
        "description": "The size of the hole in mm.",
        "scopes": ["client"],
        "image_uri": {
            "asset": "../assets/publish/hole.png"
        }, 
        "value": 2
    }
 }
 ```
 or without optional attributes:
 
 ```json
 {
    "size" : {
        "type": "numeric::number",
        "value": 2
    }
 }
 ```
 
 
 or with its shorthand version:
 
  ```json
 {
    "size" : 2
 }
 ```


# numeric::set - A set of numbers

+ **type** - The type of value, One of the six types below  *(required)*
+ **name** - A display name  *(optional)*
+ **scopes** - A list of scopes that limit the visibility of this value in the winnow pipeline *(optional)*
+ **description** - A short description  *(optional)*
+ **image_uri** - A reference to an image used to represent this range. Given as an object with a single key "asset" and a value giving a path relative to the location of this document. *(optional)*
+ **value** - A set of numbers  *(required)*

example:

 ```json
 {
    "size" : {
        "type": "numeric::set",
        "name": "Size",
        "description": "The size of the hole in mm.",
        "scopes": ["client"],
        "image_uri": {
            "asset": "../assets/publish/hole.png"
        }, 
        "value": [1, 1.5, 2.7]
    }
 }
 ```
 
 or with its shorthand version:
 
  ```json
 {
    "size" : [1, 1.5, 2.7]
 }
 ```
 
# numeric::range - A range of possible numbers

+ **type** - The type of value, One of the six types below  *(required)*
+ **name** - A display name  *(optional)*
+ **scopes** - A list of scopes that limit the visibility of this value in the winnow pipeline *(optional)*
+ **description** - A short description  *(optional)*
+ **image_uri** - A reference to an image used to represent this range. Given as an object with a single key "asset" and a value giving a path relative to the location of this document. *(optional)*
+ **max** - A maximum value  *(required)*
+ **min** - A minimum value  *(required)*

example:

 ```json
 {
    "size" : {
        "type": "numeric::range",
        "max": 3.5,
        "min": 1.0
    }
 }
 ```

# numeric::step - A range of possible numbers with discrete steps between them.

+ **type** - The type of value, One of the six types below  *(required)*
+ **name** - A display name  *(optional)*
+ **scopes** - A list of scopes that limit the visibility of this value in the winnow pipeline *(optional)*
+ **description** - A short description  *(optional)*
+ **image_uri** - A reference to an image used to represent this range. Given as an object with a single key "asset" and a value giving a path relative to the location of this document. *(optional)*
+ **max** - A maximum value  *(required)*
+ **min** - A minimum value  *(required)*
+ **step** - The size of each step  *(required)*
+ **start** - First step starts  *(required)*

example:

 ```json
 {
    "size" : {
        "type": "numeric::step",
        "max": 3.5,
        "min": 1.0,
        "start": 1.0,
        "step": 0.1
    }
 }
 ```