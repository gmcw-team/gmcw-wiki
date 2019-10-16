# Advanced Macro use

A little introduction: macros in Gamemaker are a neat compiler directive which is used to replace all occurences of a keyword with a snippet of code. For example: let's say you wanted to save and load from a configuration file. You could write the same file path in two different places, or you could avoid the potential mispelling errors and create a macro to do the work for you:

```gml
#macro CONFIG_FILE "config.ini"
```

then anywhere you type the phrase `CONFIG_FILE`, it will be replaced with the string `"config.ini"`. This comes in pretty useful when creating synonyms for constant, but we can do more...

## Overriding Functions

## Overriding Variables

## Generating Code with Custom Syntax