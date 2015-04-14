#!/bin/bash

## variable ########################################
ENV_DIR=/opt/visualops/env
PY_BIN=${ENV_DIR}/bin/python

LIB_DIR=${ENV_DIR}/lib
##---------------------------------------
if [ -d ${LIB_DIR}/python2.7 ]
then
  PYTHON="python2.7"
elif [ -d ${LIB_DIR}/python2.6 ]
then
  PYTHON="python2.6"
else
  echo "Fatal: Python2 non installed"
  exit 1
fi
echo "You are using ${PYTHON}"
##---------------------------------------
BASE_DIR=${LIB_DIR}/${PYTHON}/site-packages/opsagent/state
EXE_BIN=${BASE_DIR}/adaptor.py


JSON[1]=basic
JSON[2]=complex
JSON[3]=combo
JSON_TYPE=""


## function ########################################
function show_usage(){
  echo "========================================================="
  echo "usage: ./run.sh [type]"
  echo "---------------------------------------------------------"
  echo "[ type ] : "
  echo -e " 1 basic	( single module with required parameter test )"
  echo -e " 2 complex	( single module complex test )"
  echo -e " 3 combo	( multiple module complex test )"
  echo "========================================================="
  exit 1
}

function check_type(){
  TYPE_=$1
  if [ ${TYPE_} -lt 1 -o ${TYPE_} -gt 3 ]
  then
    echo ""
    echo "type must be 1,2 or 3"
    echo ""
    show_usage
  fi  
}

function show_module_list(){
  echo "========================================================="
  echo "module list to be test"
  echo "---------------------------------------------------------"
  cat json/module_${JSON_TYPE}.lst | grep -Ev "^#|^$" | grep -n ""
  echo "========================================================="
}

function do_all_module_test(){
  i=1
  for line in `cat json/module_${JSON_TYPE}.lst | grep -Ev "^#|^$" | awk '{print $1}'`
  do
    LEN_=`expr length ${line}`
    NSPACE_=`expr 25 - ${LEN_}`
    SPACE_=`printf "%${NSPACE_}s"`
    echo -e -n `date '+%Y-%m-%d %H:%M:%S' `" - start test ${i}:'${line}' ${SPACE_} - "
    START_TIME=`date '+%s'`

    if [ -f json/${JSON_TYPE}/${line}.json ]
    then
      cp json/${JSON_TYPE}/${line}.json ./state.json
      ${PY_BIN} ${EXE_BIN} 1>./log/${JSON_TYPE}/${line}.out 2>./log/${JSON_TYPE}/${line}.err
    
      END_TIME=`date '+%s'`
      #check result
      OUT_=`cat ./log/${JSON_TYPE}/${line}.out|wc -l`
      ERR_=`cat ./log/${JSON_TYPE}/${line}.err|wc -l`
      if [ ${JSON_TYPE} == "${JSON[1]}" ]
      then
        #only for basic test
        RLT_=`grep "^(True" ./log/${JSON_TYPE}/${line}.out|wc -l`
        if [ "${RLT_}" != "1" ]
        then
          RLT_="!!!!"
        else
          RLT_="True"
        fi
        echo -e `expr ${END_TIME} - ${START_TIME}`"s\tPASS: ${RLT_}\tout: ${OUT_}\terr: ${ERR_}"
      else
        echo -e `expr ${END_TIME} - ${START_TIME}`"s\tout: ${OUT_}\terr: ${ERR_}"
      fi

    else
      echo "!!! can not found json/${JSON_TYPE}/${line}.json !!!"
    fi
    i=`expr ${i} + 1`
  done
}


#### main ###########################################

export GREP_OPTIONS='--color=auto' 

## check parameter count
if [ $# -ne 1 ]
then
  show_usage
fi

## check type
check_type $1
case ${TYPE_} in
  1)  JSON_TYPE=${JSON[1]}
      ;;
  2)  JSON_TYPE=${JSON[2]}
      ;;
  3)  JSON_TYPE=${JSON[3]}
      ;;
esac

## show module_list to test
show_module_list ${TYPE_}

## create log dir
if [ ! -d "./log/${JSON_TYPE}" ]
then
 echo "create log dir: ./log/${JSON_TYPE}"
 mkdir -p ./log/${JSON_TYPE}
fi


## start test module
echo `date '+%Y-%m-%d %H:%M:%S' `
echo "==========================================="
do_all_module_test
echo "==========================================="
echo `date '+%Y-%m-%d %H:%M:%S' `" - done"
echo ""

