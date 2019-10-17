# Advanced Macro use

Macros in Gamemaker are what's called a *pre-compile directive*. This means that they are evaluated before your source code is compiled. Specifically, macros are used to replace all occurences of a keyword with a snippet of code.

Macros are useful for a few things. One of the popular uses it to reduce code duplication: let's say you wanted to save and load from a configuration file. You *could* write the exact same file path in two places at once. However, if you ever need to update that filepath, you will have to update it at every location you repeated it; potentially causing difficult to track bugs because of mispellings or human error. The better option would be to write a macro to do the work for you.

```gml
#macro CONFIG_FILE "config.ini"
```

Then anywhere you type the phrase `CONFIG_FILE`, it will be replaced with the string `"config.ini"`.

This comes in handy when creating synonyms for constants, but be warned! Macros are **not** constants. Take the following macro, for example. What it will **not** do is pick a random number at compile time and then replace every occurence of `RAND` with that unique random number.

```gml
#macro RAND irandom(100)
```

That covers the basics, but we can do more...

## Overriding Functions

## Overriding Variables

## Generating Code with Custom Syntax