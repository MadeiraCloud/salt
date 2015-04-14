#!/bin/bash
##
## Build script for Docker custom package
## @author: Thibault BRONCHAIN
##
## (c) 2014 MadeiraCloud LTD.
##

USAGE="$0 deb|rpm [path]"
VERSION="1.4.1"

function get_docker() {
    curl -sSL -O https://get.docker.com/builds/Linux/x86_64/docker-$VERSION
}

function deb() {
    PREV=$PWD
    if [ "$1" != "" ]; then
        cd $1
    fi
    cp docker-$VERSION deb/docker
    cd deb
    # build here
    sudo apt-get -y install make devscripts
    dpkg-buildpackage -uc -us -b
    mv $PREV/docker*{.deb,.changes} $PREV/deb/
    #

    if [ $? -eq 0 ]; then
        echo "Build succeed."
    else
        echo "Build failed."
    fi
    cd $PREV
}

function rpm() {
    PREV=$PWD
    if [ "$1" != "" ]; then
        cd $1
    fi

    # build here
    cd rpm
    cp docker.service docker
    sudo yum -y install rpm-build redhat-rpm-config make

    rm -rf ~/rpmbuild
    mkdir -p ~/rpmbuild/{RPMS,SRPMS,BUILD,SOURCES,SPECS,tmp}
    cat <<EOF >~/.rpmmacros
%_topdir   %(echo $HOME)/rpmbuild
%_tmppath  %{_topdir}/tmp
EOF
    cd ~/rpmbuild

    mkdir docker-$VERSION
    mkdir -p docker-$VERSION/usr/bin
    mkdir -p docker-$VERSION/etc/init.d
    install -m 755 $PREV/docker-$VERSION docker-$VERSION/usr/bin/docker
    install -m 755 $PREV/rpm/docker.service docker-$VERSION/etc/init.d/docker

    tar -zcvf docker-$VERSION.tar.gz docker-$VERSION/
    cp -fv docker-$VERSION.tar.gz SOURCES/

    rpmbuild -bb $PREV/rpm/docker.spec
    cp -fv ~/rpmbuild/RPMS/`uname -m`/* $PREV/rpm/
    #

    if [ $? -eq 0 ]; then
        echo "Build succeed."
    else
        echo "Build failed."
    fi
    cd $PREV
}

case $1 in
    deb)
        apt-get -y install curl
        get_docker
        deb $2
        ;;
    rpm)
        get_docker
        rpm $2
        ;;
    *)
        echo -e "syntax error\nusage: $USAGE"
        ;;
esac
