Name:           dart
Version:        3.11.4
Release:        %autorelease
Summary:        An approachable, portable, and productive language for high-quality apps on any platform

License:        BSD-3-Clause
URL:            https://dart.dev
Source0:        https://storage.googleapis.com/dart-archive/channels/stable/release/%{version}/sdk/dartsdk-linux-x64-release.zip
Source1:        https://storage.googleapis.com/dart-archive/channels/stable/release/%{version}/sdk/dartsdk-linux-arm64-release.zip

ExclusiveArch:  x86_64 aarch64

# Pre-built binaries
%global debug_package %{nil}

BuildRequires:  unzip

%description
Dart is a client-optimized language for fast apps on any platform. It provides
a productive development experience with hot reload, an expressive and flexible
type system, and native compilation to ARM and x64 machine code.

%prep
%ifarch x86_64
unzip -qo %{SOURCE0}
%endif
%ifarch aarch64
unzip -qo %{SOURCE1}
%endif

%build

%install
# Install SDK to /usr/lib/dart
install -dm 0755 %{buildroot}%{_libdir}/%{name}
cp -a dart-sdk/* %{buildroot}%{_libdir}/%{name}/

# Symlink main binary to /usr/bin
install -dm 0755 %{buildroot}%{_bindir}
ln -sf ../%{_lib}/%{name}/bin/dart %{buildroot}%{_bindir}/dart

# Remove LICENSE from SDK dir; it will be installed via %%license
rm %{buildroot}%{_libdir}/%{name}/LICENSE

%files
%license dart-sdk/LICENSE
%{_bindir}/dart
%{_libdir}/%{name}/

%changelog
%autochangelog
