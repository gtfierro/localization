#!/bin/sh
DIRNAME=`dirname $0`
BROWSER_HOME=$DIRNAME

if command -v java &>/dev/null
        then
		java -Xmx384m -Duser.country=US -Duser.language=en -Dsun.java2d.d3d=false -Dsun.java2d.noddraw=true -jar $BROWSER_HOME/lib/browser.jar $*
        else
                echo "java command is not found. Please download and install java first. ( http://www.java.com/en/download/manual.jsp )"
fi


