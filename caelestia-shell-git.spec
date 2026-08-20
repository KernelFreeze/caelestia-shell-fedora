%global base_version 2.3.0
%global commit b1c9bbd000735b987d664e1232ff85a7b90dfb1e
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20260820
# Must match M3SHAPES_REV in the upstream CMakeLists.txt. The build fetches it
# with FetchContent, which cannot reach the network in the COPR builders, so it
# is vendored as a source instead.
%global m3shapes_commit bdc327b29f95394a732baf3c9b19658ba23755b6

Name:           caelestia-shell-git
Version:        %{base_version}^%{snapdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        The desktop shell for the Caelestia dotfiles
License:        GPL-3.0-only
URL:            https://github.com/caelestia-dots/shell
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz
Source1:        https://github.com/soramanew/m3shapes/archive/%{m3shapes_commit}/m3shapes-%{m3shapes_commit}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtshadertools-devel
BuildRequires:  libqalculate-devel
BuildRequires:  aubio-devel
BuildRequires:  pipewire-devel
BuildRequires:  libcava-devel
BuildRequires:  lm_sensors-devel

Requires:       caelestia-cli-git
Requires:       quickshell-git
Requires:       ddcutil
Requires:       brightnessctl
Requires:       app2unit
Requires:       libcava
Requires:       NetworkManager
Requires:       lm_sensors
Requires:       fish
Requires:       aubio
Requires:       pipewire-libs
Requires:       glibc
Requires:       libstdc++
Requires:       material-symbols-fonts
Requires:       tuned-ppd
Requires:       rubik-fonts
Requires:       cascadia-code-nerd-fonts
Requires:       swappy
Requires:       libqalculate
Requires:       bash
Requires:       qt6-qtbase
Requires:       qt6-qtdeclarative

Provides:       caelestia-shell = %{version}-%{release}
Conflicts:      caelestia-shell < %{version}

%description
The desktop shell for the Caelestia dotfiles, packaged from the latest upstream
git snapshot.

%prep
%autosetup -n shell-%{commit} -a 1

%build
%cmake -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_INSTALL_PREFIX=/ -DINSTALL_LIBDIR=%{_libdir}/caelestia -DINSTALL_QMLDIR=%{_libdir}/qt6/qml -DVERSION=%{base_version} -DGIT_REVISION=%{commit} -DDISTRIBUTOR="Fedora COPR (package: %{name})" -DFETCHCONTENT_SOURCE_DIR_M3SHAPES_EXTERNAL=$PWD/m3shapes-%{m3shapes_commit}
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_libdir}/caelestia
%{_libdir}/qt6/qml/Caelestia
%{_libdir}/qt6/qml/M3Shapes
%config %{_sysconfdir}/xdg/quickshell/caelestia

%changelog
%autochangelog
