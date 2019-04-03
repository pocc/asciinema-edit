# Asciinema-Edit

_Rearrange and remove asciicast sections_

## Description

This script will allow you to cut out parts of your astiicast that you 
do not want. This may at some point be merged into asciinema.

## Example Usage

Use rocket.cast from the repo (also at https://asciinema.org/a/238491)
Let's pretend we like rocket animations, just without the rockets. Let's also
say that we want the exhaust to come before the picture of sky. The rocket
animation starts at 2.3s and ends at 7s. In order to specify the sky first,
use `-s 7 0`, where a 0 stop timestamp is the end of the file. Then use 
`-s 0 2.3` to specify from start to 2.3s:

    python asciicast-edit.py -r rocket.cast -w no_rocket.cast -s 7 0 -s 0 2.3
  
The result is no_rocket.cast. It is quite boring without the rocket,
but there you are.

## LICENSE

Apache 2.0, see LICENSE for more information.