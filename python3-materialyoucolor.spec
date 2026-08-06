Name:           python3-materialyoucolor
Version:        3.0.4
Release:        1%{?dist}
Summary:        Material You color generation algorithms in pure Python

License:        MIT
URL:            https://github.com/T-Dynamos/materialyoucolor-python
# Upstream publishes wheels only, no sdist, so build from the git tag instead.
Source0:        %{url}/archive/v%{version}/materialyoucolor-%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools >= 61
BuildRequires:  python3-wheel
BuildRequires:  python3-pybind11 >= 2.11.0
BuildRequires:  pybind11-devel >= 2.11.0
BuildRequires:  gcc-c++

Requires:       python3-pillow

%description
Material You color generation algorithms in pure Python.

%prep
%autosetup -n materialyoucolor-python-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files materialyoucolor

%files -f %{pyproject_files}
%license LICENSE

%changelog
%autochangelog
