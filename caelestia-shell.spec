Name:           caelestia-shell
Version:        1.5.1
Release:        1%{?dist}
Summary:        The desktop shell for the Caelestia dotfiles
License:        GPL-3.0-only
URL:            https://github.com/caelestia-dots/shell
Source0:        %{url}/releases/download/v%{version}/%{name}-v%{version}.tar.gz

ExclusiveArch:  x86_64

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  libqalculate-devel
BuildRequires:  aubio-devel
BuildRequires:  pipewire-devel
BuildRequires:  libcava-devel

Requires:       caelestia-cli
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

%description
The desktop shell for the Caelestia dotfiles.

%prep
%autosetup -n release

%build
%cmake -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_INSTALL_PREFIX=/ -DINSTALL_LIBDIR=%{_libdir}/caelestia -DINSTALL_QMLDIR=%{_libdir}/qt6/qml -DVERSION=%{version} -DGIT_REVISION=v%{version} -DDISTRIBUTOR="Fedora COPR (package: %{name})"
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_libdir}/caelestia
%{_libdir}/qt6/qml/Caelestia
%config %{_sysconfdir}/xdg/quickshell/caelestia

%changelog
%autochangelog

