Name:           alpa
Version:        1.0.0
Release:        1%{?dist}
Summary:        Integration tool with Alpa repository

License:        GPLv3
URL:            https://github.com/alpa-team/%{name}
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-click
BuildRequires:  python3-pygithub
BuildRequires:  python3-specfile

Requires:       mock
Requires:       pre-commit


%description
%{summary}


%prep
%autosetup


%generate_buildrequires
%pyproject_buildrequires -r


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files %{name}


%files -n %{name} -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/%{name}


%changelog
* Sat Mar 04 2023 Jiri Kyjovsky <j1.kyjovsky@gmail.com>
- Initial package 1.0.0
