%global commit e09ebe46ba39be6077deb3fe9a866fce278bb9f8
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20261118

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
