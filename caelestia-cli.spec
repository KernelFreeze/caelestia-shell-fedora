Name:           caelestia-cli
Version:        1.0.6
Release:        1%{?dist}
Summary:        The main cli for the Caelestia dotfiles

License:        MIT
URL:            https://github.com/caelestia-dots/cli
Source0:        %{url}/releases/download/v%{version}/caelestia-%{version}.tar.gz

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
Requires:       gpu-screen-recorder
Requires:       dconf
Requires:       cliphist
Requires:       fuzzel

Recommends:     caelestia-shell

Conflicts:      caelestia-cli-git

%description
The main cli for the Caelestia dotfiles.

%prep
%autosetup -n caelestia-%{version}

%build
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

