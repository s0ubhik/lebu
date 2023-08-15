import platform, sys, os, math

ncol   ="\033[0m"
bold   ="\033[1m"
dim    ="\033[2m"
uline  ="\033[4m"
reverse="\033[7m"
red    ="\033[31m"
green  ="\033[32m"
yellow ="\033[33m"
blue   ="\033[34m"
purple ="\033[35m"
cyan   ="\033[36m"
white  ="\033[37m"

colors = True
if platform.system == "Windows" or not colors:
    ncol=bold=dim=uline=red=green=yellow=blue=purple=cyan=white=''
