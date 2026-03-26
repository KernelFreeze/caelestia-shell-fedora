%global commit 54584294ef89979740aa9687fdc3c04d11c4b539
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20260325

Name:           rubik-fonts
Version:        0^%{snapdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        Rubik font family by Google
License:        OFL-1.1
URL:            https://github.com/google/fonts
Source0:        %{url}/raw/%{commit}/ofl/rubik/Rubik%%5Bwght%%5D.ttf#/Rubik.ttf
Source1:        %{url}/raw/%{commit}/ofl/rubik/Rubik-Italic%%5Bwght%%5D.ttf#/Rubik-Italic.ttf

BuildArch:      noarch

%description
Rubik is a sans-serif font family with slightly rounded corners.

%prep
# Font files are used directly as sources

%build
# Nothing to build

%install
install -m 0755 -d %{buildroot}%{_datadir}/fonts/%{name}
install -m 0644 -p "%{SOURCE0}" %{buildroot}%{_datadir}/fonts/%{name}/Rubik.ttf
install -m 0644 -p "%{SOURCE1}" %{buildroot}%{_datadir}/fonts/%{name}/Rubik-Italic.ttf

%files
%{_datadir}/fonts/%{name}

%changelog
%autochangelog
