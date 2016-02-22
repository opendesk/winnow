---
layout: default
---

# options and values

The options set is the core of winnows functionality. Each key in an options object is a named option and its value describes a set of possible values for this key, for example available colours or sizes - like this:

 ```json
 {
    "options":{
        "colour": ["red", "blue", "green"],
        "size": ["big", "small"],
        "wheels": [4, 6],
        "varnished": [true, false]
     }
 }
 ```

This describes the product family for a toy that comes in three colours, two sizes and can have either four or six wheels, and may or may not be varnished.

Winnow provides both a json language for defining these options and a set of operations for manipulating them. 

There are currently three main types of value for options set, numeric and boolean. In the example above ```"colour"``` is a set, ```"wheels"``` is a numeric and ```"varnished"``` is a boolean. These types can be written to include additional information and have sub-types. 

Currently there are seven types and sub-types of value you can use:

+ **set::string**
+ **numeric::number**
+ **numeric::set**
+ **numeric::range**
+ **numeric::step**
+ **boolean**

## set values

Set value types are used to express discrete optional variation in a product attribute. There are two set types, string and resource. String values are used to express any arbitrary values types, and resource types refer to other winnow resource documents by path.

### set::string

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
        "type": "set::string",
        "name": "colour",
        "description": "Please choose one of the colours",
        "default": "red",
        "values": [
            {
                "type": "string",
                "name": "Red",
                "description": "the colour red",
                "image_uri": "http://something.com/khgfdkyg.png",
                "value": "red",
            },
            {
                "type": "string",
                "name": "Blue",
                "description": "the colour blue",
                "image_uri": "http://something.com/khgfdkyg.png",
                "value": "blue"
            }
        ]
    }
}
```

You can use shorthand syntax for just the values:

 ```json
{
    "colour": {
        "type": "set::string",
        "name": "colour",
        "description": "Please choose one of the colours",
        "default": "red",
        "values": ["red", "blue"]
    }
}
```

Or more concisely still you can use shorthand syntax for the whole object:

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
    "type": "set::string",
    "name": "colour",
    "description": "Please choose one of the colours",
    "default": "red",
    "values": [
        {
            "type": "string",
            "name": "Red",
            "description": "the colour red",
            "image_uri": "http://something.com/khgfdkyg.png",
            "value": "red",
            "options":{
                "type": "set::string",
                "name": "varnish",
                "description": "Please choose varnish type",
                "default": "matt",
                "values":[
                    {
                    "type": "string",
                    "name": "Matt",
                    "description": "Use matt varish",
                    "image_uri": "http://something.com/khgfdkyg.png",
                    "value": "matt",
                    },
                    {
                    "type": "string",
                    "name": "Gloss",
                    "description": "Use gloww varish",
                    "image_uri": "http://something.com/khgfdkyg.png",
                    "value": "gloss",
                    }
                ]
            }
        },
        {
            "type": "string",
            "name": "Blue",
            "description": "the colour blue",
            "image_uri": "http://something.com/khgfdkyg.png",
            "value": "blue"
        }
    ]
}
```

## numeric values

Numeric value types can be used to express possible variation of a number and all four numeric value types can be used interchangeably and compared to each other.

### numeric::number

A single number

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


### numeric::set

A set of numbers

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
 
### numeric::range - A range of possible numbers

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

### numeric::step

A range of possible numbers with discrete steps between them.

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

### boolean

A boolean true or false value

+ **type** - The type of value, One of the six types below  *(required)*
+ **name** - A display name  *(optional)*
+ **scopes** - A list of scopes that limit the visibility of this value in the winnow pipeline *(optional)*
+ **description** - A short description  *(optional)*
+ **image_uri** - A reference to an image used to represent this range. Given as an object with a single key "asset" and a value giving a path relative to the location of this document. *(optional)*
+ **value** - true, false or either  *(required)*

A boolean value is normally written as ```[true, false]```. The long version looks like this:


 ```json
 {
    "varnished" : {
        "type": "boolean",
        "name": "Varnished",
        "scopes": ["client"],
        "description": 'Is it varnished",
        "value": [true, false]
    }
 }
 ```
 
 And a shorthand one like this:

 ```json
 {
    "varnished" : [true, false]
 }
 ```
