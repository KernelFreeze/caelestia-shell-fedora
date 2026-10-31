Name:           qtengine
Version:        0.2.4
Release:        1%{?dist}
Summary:        Qt platform theme using the KDE color scheme format

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
# Qt5ThemeSupport is only shipped as a static library
BuildRequires:  qt5-qtbase-static
BuildRequires:  qt5-qtquickcontrols2-devel
BuildRequires:  kf5-kconfig-devel
BuildRequires:  kf5-kconfigwidgets-devel
BuildRequires:  kf5-kiconthemes-devel

# Qt6
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  kf6-kconfig-devel
BuildRequires:  kf6-kcolorscheme-devel
BuildRequires:  kf6-kiconthemes-devel

%description
A Qt6 and Qt5 platform theme that reads a KDE color scheme, icon theme,
widget style and fonts from a single JSON file. Enable it with
QT_QPA_PLATFORMTHEME=qtengine.

%prep
%autosetup

%build
%cmake -G Ninja \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DQT5_PLUGINDIR=%{_qt5_plugindir} \
    -DQT6_PLUGINDIR=%{_qt6_plugindir}
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libqt5engine-common.so
%{_libdir}/libqt6engine-common.so
%{_qt5_plugindir}/platformthemes/libqt5engine-plugin.so
%{_qt5_plugindir}/styles/libqt5engine-style.so
%{_qt6_plugindir}/platformthemes/libqt6engine-plugin.so
%{_qt6_plugindir}/styles/libqt6engine-style.so

%changelog
%autochangelog
