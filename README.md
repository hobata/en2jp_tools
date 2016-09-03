Exuberand Ctags:
ctagc *c

vi:
Jump: [CTRL] +"]"
Return:  [CTRL] +"T"

Make tag files.
find `pwd` -type f -name "*.[ch]" -o -name "*.[sS]" | sed -e 's/^/"/' -e 's/$/"/' | xargs /usr/bin/ctags -a

.vimrc
set tage=./tags,tags,/cygdrive/c/usr/linux/linux-2.6.36/tags

keyword search
find -name "*.[csh]" -type f | xargs grep -n key_word /dev/null | less

