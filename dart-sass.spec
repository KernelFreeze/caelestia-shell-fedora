%global _sass_version 3.2.0
%global _buf_version 1.66.1

Name:           dart-sass
Version:        1.98.0
Release:        %autorelease
Summary:        Sass makes CSS fun again

License:        MIT
URL:            https://sass-lang.com
Source0:        https://github.com/sass/dart-sass/archive/%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/sass/sass/archive/embedded-protocol-%{_sass_version}/sass-embedded-protocol-%{_sass_version}.tar.gz
Source2:        https://github.com/bufbuild/buf/releases/download/v%{_buf_version}/buf-Linux-x86_64
Source3:        https://github.com/bufbuild/buf/releases/download/v%{_buf_version}/buf-Linux-aarch64
Source4:        %{name}-%{version}-pub-cache.tar.gz

ExclusiveArch:  x86_64 aarch64

# Dart-compiled binary has no debug sources
%global debug_package %{nil}

BuildRequires:  dart
BuildRequires:  git

Provides:       sass
Conflicts:      rubygem-sass

%description
Sass makes CSS fun again. Sass is an extension of CSS, adding nested rules,
variables, mixins, selector inheritance, and more. It is translated to
well-formatted, standard CSS using the command line tool or a plugin for your
build system.

%prep
%autosetup -n %{name}-%{version}

# Extract embedded protocol source
tar -xzf %{SOURCE1} -C %{_builddir}
mkdir -p build
ln -sf %{_builddir}/sass-embedded-protocol-%{_sass_version} build/language

# Set up buf
%ifarch x86_64
install -Dpm 0755 %{SOURCE2} %{_builddir}/bin/buf
%endif
%ifarch aarch64
install -Dpm 0755 %{SOURCE3} %{_builddir}/bin/buf
%endif
export PATH="%{_builddir}/bin:$PATH"

# Extract vendored pub cache
tar -xzf %{SOURCE4} -C %{_builddir}
export PUB_CACHE="%{_builddir}/pub-cache"

# Disable analytics
dart --disable-analytics

# Resolve dependencies offline
dart pub get --offline

%build
export PATH="%{_builddir}/bin:$PATH"
export PUB_CACHE="%{_builddir}/pub-cache"

UPDATE_SASS_PROTOCOL=false dart run grinder protobuf
dart compile exe \
  -Dversion=%{version} \
  -Dprotocol-version=$(cat build/language/spec/EMBEDDED_PROTOCOL_VERSION) \
  -o sass \
  bin/sass.dart

%install
install -Dpm 0755 sass %{buildroot}%{_bindir}/sass
install -Dpm 0644 build/language/spec/embedded_sass.proto %{buildroot}%{_datadir}/%{name}/embedded_sass.proto

%files
%license LICENSE
%{_bindir}/sass
%{_datadir}/%{name}/embedded_sass.proto

%changelog
%autochangelog
