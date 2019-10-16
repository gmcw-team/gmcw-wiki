# Advanced Macro use

## Introduction

Macros in Gamemaker are a pretty neat compiler directive which can be used to replace all occurences of a keyword with a snippet of code. For example: let's say you wanted to save and load from a configuration file. You could write the same file path in two different locations. However, this has the potential to cause silly errors because of mispelling and human error. The other, better, option would be to write a macro to do the work for you.

```gml
#macro CONFIG_FILE "config.ini"
```

Then anywhere you type the phrase `CONFIG_FILE` in your code, it will be replaced with the string `"config.ini"`.

This comes in handy when creating synonyms for constants, but be warned: macros are **not** constants. Take the following macro, for example. It will return a new random number (between 0 and 100) for every occurence of `RAND`.

```gml
#macro RAND irandom(100)
```

That covers the basics, but we can do more...

## Overriding Functions

## Overriding Variables

## Generating Code with Custom Syntax