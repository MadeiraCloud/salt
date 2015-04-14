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
  echo "usage: ./step.sh [type]"
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
  echo "usage: ./step.sh ${TYPE_} n #n>=1"
  echo "---------------------------------------------------------"
  echo "[ n ] : "
  cat json/module_${JSON_TYPE}.lst | grep -Ev "^#|^$" | grep -n ""
  echo "========================================================="
  exit
}


function show_json(){
  
  if [ `which underscore| wc -l` -eq 1 ]
  then
    echo "###################################"
    echo "pretty json"
    echo "###################################"
    if [ `which colout| wc -l` -eq 1 ]
    then
      cat $1 | underscore print --outfmt pretty | colout "True|False" red
    else
      cat $1 | underscore print --outfmt pretty
    fi
  else
    install_underscore_cli
    cat $1
  fi

}

function install_underscore_cli(){
  echo "#################################################################"
  echo "to install underscore-cli, run the following two command lines:"
  echo "  yum install nodejs"
  echo "  npm install -g underscore-cli"
  echo "#################################################################"
}

function show_result(){

  if [ `which colout| wc -l` -eq 1 ]
  then
    $1 $2 | colout "True|False" red
  else
    install_colout
    $1 $2
  fi

}

function install_colout(){
  echo "#################################################################"
  echo "to install colout, run the following command line:"
  echo "  pip install colout"
  echo "#################################################################"
}

function do_module_test(){
  i=1
  for line in `cat json/module_${JSON_TYPE}.lst | grep -Ev "^#|^$" | awk '{print $1}'`
  do
    if [ "${i}" == "${NO_}" ]
    then
      echo `date '+%Y-%m-%d %H:%M:%S' `" - start test '${line}'"
      if [ -f json/${JSON_TYPE}/${line}.json ]
      then
        echo "- test json ---------------------------------------"
        cp json/${JSON_TYPE}/${line}.json ./state.json
        show_json json/${JSON_TYPE}/${line}.json
        echo "- result ---------------------------------------"
        show_result "${PY_BIN}" "${EXE_BIN}"
      else
        echo "!!! can not found json/${JSON_TYPE}/${line}.json !!!"
      fi
      break
    fi
    i=`expr $i + 1`
  done
}

#### main ###########################################

export GREP_OPTIONS='--color=auto' 

## check parameter count
if [ $# -ne 1 -a $# -ne 2 ]
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

##show module list for type
if [ $# -eq 1 ]
then
  show_module_list ${TYPE_}
fi

## module number
NO_=$2

## start test module
echo `date '+%Y-%m-%d %H:%M:%S' `
echo "==========================================="
do_module_test
echo "==========================================="
echo `date '+%Y-%m-%d %H:%M:%S' `" - done"
echo ""

