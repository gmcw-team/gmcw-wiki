# Advanced Macro use

Macros in Gamemaker are what's called a *compiler directive*; this means that they give the compiler additional information about how to interpret your source code. Specifically, macros are used to replace all occurences of a keyword with a snippet of code.

Macros are useful for a few things: the most popular of these is to reduce code duplication by creating synonyms for frequently used constants. Let's say you wanted to save and load from a configuration file. You *could* write the exact same file path in two places at once, but imagine if you ever need to update that filepath; you would have to manually update every occurence of that filepath, potentially causing difficult to track bugs because of mispellings or human error.

The better option would be to write a macro (`CONFIG_FILE`) to do the work for you. Then, anywhere you type the phrase `CONFIG_FILE`, the compiler will automatically replace it with the string `"config.ini"`.

```gml
#macro CONFIG_FILE "config.ini"
```

But be warned! Macros are **not** constants. Notice the macro below. Every time you use this macro, it will *actually* create a new instance of the `obj_player` object. So, if you had one-hundred occurences of the phrase `PLAYER`, you would have one-hundred *unique* instances of the `obj_player` object.

```gml
#macro PLAYER instance_create_depth(0, 0, 0, obj_player)
```

That covers the basics, but we can do more...

## Unhygienic Macros

## Overriding Functions

## Overriding Variables

## Generating Code with Custom Syntax