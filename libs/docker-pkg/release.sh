#!/bin/bash
##
## Release script for Docker custom package
## @author: Thibault BRONCHAIN
##
## (c) 2014 MadeiraCloud LTD.
##

DEB="docker_1.5.0-0_all.deb"
RPM="docker-1.5.0-1.x86_64.rpm"

GPG_PRIVATE_PATH=${HOME}/.ssh/keys/madeira.gpg.private.key
gpg --allow-secret-key-import --import ${GPG_PRIVATE_PATH}
gpg --sign $DEB
gpg --sign $RPM
cksum $RPM.gpg > $RPM.gpg.cksum
cksum $DEB.gpg > $DEB.gpg.cksum
cksum $RPM > $RPM.cksum
cksum $DEB > $DEB.cksum
