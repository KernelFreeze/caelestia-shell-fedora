Name:           python3-materialyoucolor
Version:        3.0.2
Release:        1%{?dist}
Summary:        Material You color generation algorithms in pure Python

License:        MIT
URL:            https://github.com/T-Dynamos/materialyoucolor-python
Source0:        %{pypi_source materialyoucolor}

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
%autosetup -n materialyoucolor-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files materialyoucolor

%files -f %{pyproject_files}
%license LICENSE

%changelog
%autochangelog
