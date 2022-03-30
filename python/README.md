https://stackoverflow.com/questions/15610183/if-else-statements-in-antlr-using-listeners

https://github.com/antlr/antlr4/blob/master/doc/getting-started.md

## Build the visitor scaffolding

antlr4 -Dlanguage=Python3 ToggleRuleGrammer.g4 -visitor -o dist


## Setup
export CLASSPATH=".:/usr/local/lib/antlr-4.9.2-complete.jar:$CLASSPATH"
alias antlr4='java -Xmx500M -cp "/usr/local/lib/antlr-4.9.2-complete.jar:$CLASSPATH" org.antlr.v4.Tool'
alias grun='java -Xmx500M -cp "/usr/local/lib/antlr-4.9.2-complete.jar:$CLASSPATH" org.antlr.v4.gui.TestRig'