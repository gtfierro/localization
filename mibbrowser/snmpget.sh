#!/bin/sh
DIRNAME=`dirname $0`
BROWSER_HOME=$DIRNAME
java -Xmx384m -cp $BROWSER_HOME/lib/browser.jar com.ireasoning.app.mibbrowser.SnmpGet $*
