%global base_version 1.1.2
%global commit 5c5c0a817004a16222dd19a04b8b6fb6492f65f7
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20260802
%global python_snapshot_version %{base_version}.post%{snapdate}+git%{shortcommit}

Name:           caelestia-cli-git
Version:        %{base_version}^%{snapdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        The main cli for the Caelestia dotfiles

License:        GPL-3.0-only
URL:            https://github.com/caelestia-dots/cli
Source0:        %{url}/archive/%{commit}/%{name}-%{commit}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-build
BuildRequires:  python3-installer
BuildRequires:  python3-hatchling
BuildRequires:  python3-hatch-vcs

Requires:       python3
Requires:       python3-pillow
Requires:       python3-materialyoucolor
Requires:       libnotify
Requires:       swappy
Requires:       grim
Requires:       dart-sass
Requires:       app2unit
Requires:       wl-clipboard
Requires:       slurp
Requires:       gpu-screen-recorder-ui
Requires:       dconf
Requires:       cliphist
Requires:       fuzzel

Recommends:     caelestia-shell-git

Provides:       caelestia-cli = %{version}-%{release}
Conflicts:      caelestia-cli < %{version}

%description
The main cli for the Caelestia dotfiles, packaged from the latest upstream git
snapshot.

%prep
%autosetup -n cli-%{commit}

%build
export SETUPTOOLS_SCM_PRETEND_VERSION=%{python_snapshot_version}
%python3 -m build --wheel --no-isolation

%install
%python3 -m installer --destdir=%{buildroot} dist/*.whl
install -Dm644 completions/caelestia.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/caelestia.fish

%files
%license LICENSE
%{python3_sitelib}/caelestia*/
%{_bindir}/caelestia
%{_datadir}/fish/vendor_completions.d/caelestia.fish

%changelog
%autochangelog
