#! /usr/bin/env bash

remote="nuosen248"
remote_home="/data2/rbamb"
remote_working_directory="$remote_home/fun/UsabilityTest"

rsync -vazP \
  --exclude=".git" \
  $PWD "$remote:$remote_home/fun/"

# ssh -tt "$remote" "source ~/.bash_profile && cd $remote_working_directory && python3 do.py c 1-100 loc"
ssh -tt "$remote" "source ~/.bash_profile && cd $remote_working_directory && python3 diagram.py"
# ssh -tt "$remote" "source ~/.bash_profile && cd $remote_working_directory && java -jar tools/ENRE/ENRE-cpp.jar repo/RIOT RIOT"
