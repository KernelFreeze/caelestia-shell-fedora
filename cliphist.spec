Name:           cliphist
Version:        0.7.0
Release:        %autorelease
Summary:        Wayland clipboard manager with support for multimedia

License:        GPL-3.0-only
URL:            https://github.com/sentriz/cliphist
Source0:        https://github.com/sentriz/cliphist/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.gz

BuildRequires:  golang
BuildRequires:  golang-etcd-bbolt-devel
BuildRequires:  golang-github-rivo-uniseg-devel
BuildRequires:  golang-x-image-devel
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)

%global common_description %{expand:
Wayland clipboard manager with support for multimedia.}

%description %{common_description}

%prep
%autosetup -p1 -n %{name}-%{version}

%build
# Extract vendor tarball (contains only flagconf since it's not in Fedora yet)
tar -xzf %{SOURCE1}

# Build using system GOPATH
mkdir -p _build/bin
export GOPATH=$(pwd)/_build:%{gopath}
go build -o _build/bin/%{name} .

%install
install -dm 0755 %{buildroot}%{_bindir}
install -pm 0755 _build/bin/%{name} %{buildroot}%{_bindir}/

# Install documentation
install -dm 0755 %{buildroot}%{_docdir}/%{name}
install -pm 0644 CHANGELOG.md %{buildroot}%{_docdir}/%{name}/
install -pm 0644 readme.md %{buildroot}%{_docdir}/%{name}/
install -pm 0644 version.txt %{buildroot}%{_docdir}/%{name}/

# Install license
install -dm 0755 %{buildroot}%{_licensedir}/%{name}
install -pm 0644 LICENSE %{buildroot}%{_licensedir}/%{name}/

%files
%{_bindir}/%{name}
%doc CHANGELOG.md readme.md version.txt
%license LICENSE

%changelog
%autochangelog

