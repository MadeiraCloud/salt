##
## Build spec file for Docker custom package
## @author: Thibault BRONCHAIN
##
## (c) 2014 MadeiraCloud LTD.
##

Name:           docker
Version:        1.5.0
Release:        1
Summary:        An open source project to pack, ship and run any application as a lightweight container

Group:          Applications/System
License:        Apache-2.0
URL:            http://www.docker.io/
Source:         %{name}-%{version}.tar.gz

Requires:       shadow-utils, libcgroup

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

# no debug as no build
%define         __spec_install_post %{nil}
%define         debug_package %{nil}
%define         __os_install_post %{_dbpath}/brp-compress
%define         archivedir docker-%{version}
%define         realname docker


%description
Docker is an open-source engine that automates the deployment of any application as a lightweight, portable, self-sufficient container that will run virtually anywhere.


%prep
%setup -q


%build
# no build


%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}
# in builddir
cp -a * %{buildroot}


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{_bindir}/docker
%{_sysconfdir}/init.d/docker


%post
# mount cgroups
if grep -v '^#' /etc/fstab | grep -q cgroup; then
    echo 'cgroups mounted from fstab, not mounting /sys/fs/cgroup'
else
    # kernel provides cgroups?
    if [ -e /proc/cgroups ]; then
        # if we don't even have the directory we need, something else must be wrong
        if [ -d /sys/fs/cgroup ]; then
            # mount /sys/fs/cgroup if not already done
            if ! mountpoint -q /sys/fs/cgroup; then
	        mount -t tmpfs -o uid=0,gid=0,mode=0755 cgroup /sys/fs/cgroup
            fi
            cd /sys/fs/cgroup
            # get/mount list of enabled cgroup controllers
            for sys in $(awk '!/^#/ { if ($4 == 1) print $1 }' /proc/cgroups); do
	        mkdir -p $sys
	        if ! mountpoint -q $sys; then
		    if ! mount -n -t cgroup -o $sys cgroup $sys; then
			rmdir $sys || true
		    fi
	        fi
            done
        fi
    fi
fi
# create group
getent group %{realname} >/dev/null || groupadd -r %{realname}
# install systemd service
if [ -d "/usr/lib/systemd" ]; then
    mkdir -p /usr/lib/systemd/system
    cat <<EOF > /usr/lib/systemd/system/docker.service
[Unit]
Description=Docker

[Service]
Type=oneshot
ExecStart=/etc/init.d/docker start
ExecStop=/etc/init.d/docker stop
ExecRestart=/etc/init.d/docker restart
ExecStatus=/etc/init.d/docker status
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
    chmod 755 /usr/lib/systemd/system/docker.service
fi


%changelog
* Thu Mar 19 2015 Thibault Bronchain <thibault@visualops.io> - 1.5.0
- Update to v1.5.0
* Tue Jan 6 2015 Thibault Bronchain <thibault@visualops.io> - 1.4.1
- Update to v1.4.1
* Mon Nov 17 2014 Thibault Bronchain <thibault@visualops.io> - 1.3.1
- Update to v1.3.1
* Mon Sep 1 2014 Thibault Bronchain <thibault@visualops.io> - 1.2.0
- Create package
