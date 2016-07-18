Productivity Clock
==================

A simple GNOME indicator widget showing a stopwatch for keeping track of your
productive hours.

Here's how it works:

 * Start the clock when you start doing productive work. The definition of
   productivity is up to you :bowtie:
 * Every 15 minutes, the clock stops. If you're still being productive, restart
   it (one click/drag of the mouse).
 * Between 11pm and 7am, the clock stops (if you're being productive) or runs
   backward (if not), to encourage a regular sleep schedule. [Pull requests
   appreciated to make this configurable!]
 * In addition to the total amount of productive time for the day, the clock
   shows how the current amount compares to previous days (as a percentile).

Screenshots
-----------

![Clocking in](/screenshots/start.png)
![Clocking out](/screenshots/stop.png)

Installing
----------

Clone the repository (anywhere on your machine, but it will need to stay
there):

::

    git clone https://github.com/futurulus/productivity.git
    cd productivity

Fire up the clock:

::

    ./productivity-indicator

Set it up to run on startup (you can also do this manually via the Startup
Applications preferences window):

::

    ./autostart
