#!/bin/sh
DIRNAME=`dirname $0`
BROWSER_HOME=$DIRNAME
java  -Xmx384m  -Duser.country=US -Duser.language=en -classpath $BROWSER_HOME/browser.jar  com.ireasoning.server.NetworkServer $*
