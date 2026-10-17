Name:           qtengine
Version:        0.2.2
Release:        1%{?dist}
Summary:        QT Platform Theme made easy.

License:        BSD-2-Clause
URL:            https://github.com/kosslan/qtengine
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  extra-cmake-modules

# Qt5
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtbase-private-devel
BuildRequires:  qt5-qtbase-static
BuildRequires:  qt5-qtquickcontrols2-devel
BuildRequires:  kf5-kconfig-devel
BuildRequires:  kf5-kconfigwidgets-devel
BuildRequires:  kf5-kiconthemes-devel

# Qt6
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  kf6-kconfig-devel
BuildRequires:  kf6-kcolorscheme-devel
BuildRequires:  kf6-kiconthemes-devel

%description
%{summary}

%prep
%autosetup

%build
%cmake \
    -G Ninja \
    -DCMAKE_BUILD_TYPE:STRING=Release \
    -DCMAKE_SKIP_INSTALL_RPATH=ON
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_lib}
%cmake_build

%install
%cmake_install
# Upstream hardcodes /usr/lib/qt{5,6}/plugins; Fedora's Qt only searches
# /usr/lib64/qt{5,6}/plugins, so move the plugins there.
for qt in qt5 qt6; do
    if [ -d %{buildroot}%{_prefix}/lib/$qt ]; then
        mkdir -p %{buildroot}%{_libdir}
        mv %{buildroot}%{_prefix}/lib/$qt %{buildroot}%{_libdir}/$qt
    fi
done

%files
%{_libdir}/libqt*engine-common.so*
%{_libdir}/qt6/plugins/platformthemes/libqt6engine-plugin.so
%{_libdir}/qt6/plugins/styles/libqt6engine-style.so
%{_libdir}/qt5/plugins/platformthemes/libqt5engine-plugin.so
%{_libdir}/qt5/plugins/styles/libqt5engine-style.so
%license LICENSE
