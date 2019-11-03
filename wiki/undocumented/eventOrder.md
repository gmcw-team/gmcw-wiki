# Event Order

At the heart of GameMaker is an event loop. A loop that calls the event code for your instances in sequence. While you, the game dev, provide the code that goes into events, it's this event loop inside GameMaker that decides what order to execute those events in.

The exact order is largely undocumented. It is described briefly in incomplete form [here](https://docs2.yoyogames.com/source/_build/2_interface/1_editors/events/index.html) and [here](https://docs2.yoyogames.com/source/_build/2_interface/1_editors/events/draw_events.html). However the details are more nuaunced than this.

The following is an attempt to demystify and document the event order:

## Event Loop events
The following events are triggered by GameMaker's event loop as part of the lifecycle of a game.

| Event                | When does it run?           | Description |
| -------------------- | --------------------------- | ----------- |
| PreCreate            | on instance creation        | Object/Instance variables form the variable editor are initialized    |
| Create event         | on instance creation        | The Create event code from the object editor. The order of how these are run can be changed using the Instance Creation Order in the room editor |
| Create code          | on instance creation        | The Instance Creation Code from the room editor |
| Game Start event     | once on entering first room | The Game Start event from the object editor, only runs once upon entering the first room in the game when the game starts, including after `game_restart()` |
| Room Creation code   | on entering room            | The Room Creation code from the room editor |
| Room Start event     | on entering room            | The Room Start event from the object editor |
| Begin Step event     | every frame                 | The Begin Step event from the object editor |
| Alarm events         | when an alarm reaches 0     | The Alarm events from the object editor |
| Keyboard events      | on matching key press       | The Keyboard events from the object editor |
| Mouse events         | on matching mouse press     | The Mouse events from the object editor |
| Async events         | when there are async events | Despite its name, most (all?) async events actually run here, between Begin Step and Step. They only run when there is an async trigger, but could run multple times. |
| Step event           | every frame                 | The Step event from the object editor. Built-in motion variables like `speed` and `direction` are processed after this event, and `xprevious` and `yprevious` are set before this event also |
| Collision events     | on matching collision       | The Collision events from the object editor. |
| End Step event       | every frame                 | The Step event from the object editor. |
| Pre Draw event       | every frame                 | The Pre Draw event from the object editor. This events draws onto the back buffer by default. |
| Draw Begin event     | for each viewport           | The Draw Begin event from the object editor. This event draws onto the application_surface or view surface by default, and if viewport clearing is turned on, the viewport will be cleared before this event |
| Draw event           | for each viewport           | The Draw event from the object editor. This event draws onto the application_surface or view surface by default. If this event is not provided, the object's default draw will be used |
| Draw End event       | for each viewport           | The Draw End event from the object editor. This event draws onto the application_surface or view surface by default |
| Post Draw event      | every frame                 | The Post Draw event from the object editor. This event draws onto the back buffer by default. The application_surface is drawn onto the back buffer after this event if automatic application_surface drawing is turned on |
| Draw GUI Begin event | every frame                 | The Draw GUI Begin event from the object editor. This event draws onto the back buffer by default, at the resolution set by `display_set_gui_size()` |
| Draw GUI event       | every frame                 | The Draw GUI event from the object editor. This event draws onto the back buffer by default, at the resolution set by `display_set_gui_size()` |
| Draw GUI End event   | every frame                 | The Draw GUI End event from the object editor. This event draws onto the back buffer by default, at the resolution set by `display_set_gui_size()` |

## User-triggered events
The following events are never triggered by GameMaker's event loop, and therefore run only when called by user code

| Event                | When does it run?           | Description |
| -------------------- | --------------------------- | ----------- |
| Destroy              | on `instance_destroy()`     | The Destroy event from the object editor. Only when `instance_destroy()` is called, and only when the second (optional) argument of that function is `true` (this is the default behaviour if the second argument is not supplied). |
| User events          | on `event_user()`           | The User events from the object editor. |

## Uncertainties/TODO
There are some uncertainties still in the exact order of some of the events above, and furthur study is necessary (please edit this page if you do the experiments):
* Exact order of: Alarm, Async, Keyboard, and Mouse events
* Exact order of all the async events
* Where `xprevious` and `yprevious` get set. This needs to be confirmed
* When does Window Resize happen?
* When does Cleanup happen?
* When do Gesture Events happen?
* When do Outside Room/IntersectBoundary events happen?
* When do Animation events happen?
* When do Path Ended event happen?