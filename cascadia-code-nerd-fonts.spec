Name:           cascadia-code-nerd-fonts
Version:        3.4.0
Release:        1%{?dist}
Summary:        Cascadia Code patched with Nerd Fonts icons
License:        OFL-1.1
URL:            https://github.com/ryanoasis/nerd-fonts
Source0:        %{url}/releases/download/v%{version}/CascadiaCode.tar.xz

BuildArch:      noarch

%description
Cascadia Code font patched with Nerd Fonts glyphs for terminal and editor use.

%prep
%autosetup -c

%build
# Nothing to build

%install
install -m 0755 -d %{buildroot}%{_datadir}/fonts/%{name}
install -m 0644 -p *.ttf %{buildroot}%{_datadir}/fonts/%{name}/

%files
%{_datadir}/fonts/%{name}

%changelog
%autochangelog
