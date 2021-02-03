#!/bin/bash

/init.sh &
exec /usr/local/bin/update-params.sh /usr/sbin/init
