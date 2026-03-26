%global _sass_version 3.2.0

Name:           dart-sass
Version:        1.98.0
Release:        %autorelease
Summary:        Sass makes CSS fun again

License:        MIT
URL:            https://sass-lang.com
Source0:        https://github.com/sass/dart-sass/archive/%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/sass/sass/archive/embedded-protocol-%{_sass_version}/sass-embedded-protocol-%{_sass_version}.tar.gz

BuildRequires:  dart
BuildRequires:  buf
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

mkdir -p build
ln -sf %{_builddir}/sass-embedded-protocol-%{_sass_version} build/language

# Extract embedded protocol source
tar -xzf %{SOURCE1} -C %{_builddir}

# Disable analytics
dart --disable-analytics

# Download dependencies
dart pub get

%build
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
