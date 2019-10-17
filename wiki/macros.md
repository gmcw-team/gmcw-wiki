# Advanced Macro use

Macros in Gamemaker are what's called a _compiler directive_; this means that they give the compiler additional information about how to interpret your source code. Specifically, macros are used to replace all occurences of a keyword with a snippet of code.

Macros are useful for a few things: the most popular of these is to reduce code duplication by creating synonyms for frequently used constants. Let's say you wanted to save and load from a configuration file. You _could_ write the exact same file path in two places at once, but imagine if you ever need to update that filepath; you would have to manually update every occurence of that filepath, potentially causing difficult to track bugs because of mispellings or human error.

The better option would be to write a macro (`CONFIG_FILE`) to do the work for you. Then, anywhere you type the phrase `CONFIG_FILE`, the compiler will automatically replace it with the string `"config.ini"`.

```gml
#macro CONFIG_FILE "config.ini"
```

But be warned! Macros are **not** constants. Notice the macro below. Every time you use this macro, it will *actually* create a new instance of the `obj_player` object.

```gml
#macro PLAYER instance_create_depth(0, 0, 0, obj_player)
```

So, if you had one-hundred occurences of the phrase `PLAYER`, you would have one-hundred _unique_ instances of the `obj_player` object.

That covers the basics, but we can do more...

## Overriding Functions

Gamemaker has a vague sense of a 'standard library', i.e. it has built-in functions which are written in the engine's native code. Perhaps you've wanted to replace a native function with your own implementation? Although Gamemaker doesn't support method overriding outside of object events, we can actually abuse macros to replace all occurences of a native function with our own function!

To do this, it is as simple as creating a macro with the same name as the native function, then in the body of the macro we write the function we want it to be replaced with. Consider a custom function `log`, which writes a message to a log file called `"debug.log"`. We can then use it to override the native function `show_debug_message` by creating the following macro:

```gml
#macro show_debug_message log
```

Now, every time you call `show_debug_message`, you will actually be calling `log`; writing the message to a log file instead of to the console.

The benefit of this method is you can seemlessly plug-in systems into existing projects with minimal interference. Additionally, because your entire codebase wont have to depend on a single `log` function, if you decide you no longer want or need to log debug messages, it is as simple as removing the macro and everything magically goes back to normal!

However, this is a one-way trip. Unfortunately, overriding a native function means you wont be able to use the native implementation of that function again until you stop overriding it.

## Overriding Variables

The idea of overriding native functions can be extended to overriding built-in variables and constants. Let's say you want to change the colour of `c_red` to a [better shade](https://www.color-hex.com/color/d15864)*. We can then create a macro to change all occurences of `c_red` to this new colour.

```gml
#macro c_red 0x6458D1
```

This has the same benefits and limitations as overriding functions, i.e. you cannot use the original colour unless you stop overriding it.

_*Since Gamemaker stores colors as BGR instead of as RGB, the hex code of the new colour will be `0x6458D1` instead of the `0xD15864` displayed on the linked page._

## The Precedence Problem

Consider the following macro.

```gml
#macro TOTAL 5 + 8
```

Now suppose it is used in an expression such as:

```gml
var a = 4 * TOTAL;
```

You might expect the value of `a` to be `4 * (5 + 8)` because of precedence rules. However, due to the behaviour of macros, this is not the case! The compiler will expand the previous expression into `4 * 5 + 8`, which is not the desired result. To obtain the result we want, the expression inside the body of the macro should be wrapped in a grouping as follows:

```gml
#macro TOTAL (5 + 8)
```

This would now give the desired result of `4 * (5 + 8)`.

Much like the how macros can be abused to simulate function overriding, this behaviour can be abused for array indexing. Suppose you have an array `a` of the form `[x1, y1, x2, y2, ...]`. To index this array, you may use the following code:

```gml
var xpos = a[i * 2 + 0];
var ypos = a[i * 2 + 1];
```

This will get the x and y positions of the pair at the index `i`.

Now, consider the following code:

```gml
#macro XPOS 2 + 0
#macro YPOS 2 + 1

var xpos = a[i * XPOS];
var xpos = a[i * YPOS];
```

Notice that there are no parenthesis around the expressions in the macro bodies. These macros will be expanded by the compiler into code that is equivalent to the previous snippet.

## The Hygiene Problem

Macros are _non-hygienic_. This means that macros may create and access variables from outside of its scope. For example, consider the following snippet of code:

```gml
#macro MAKE_VAR var a = 2

MAKE_VAR;
show_message(a);
```

If macros were hygienic, this code would throw an error because the variable `a` does not exist. Since this is not the case, after the compiler expands the code into the following snippet, it becomes trivial that no error will occur.

```gml
var a = 2;
show_message(a);
```