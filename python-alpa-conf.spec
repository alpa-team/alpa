%global srcname alpa-conf


Name:           python-%{srcname}
Version:        1.0.0
Release:        1%{?dist}
Summary:        Wrapper around configuration files for packit and alpa

License:        GPLv3
URL:            https://github.com/alpa-team/%{srcname}
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-pyyaml


%description
%{summary}


%package -n     python3-%{srcname}
Summary:        %{summary}


%description -n python3-%{srcname}
%{summary}


%prep
%autosetup


%generate_buildrequires
%pyproject_buildrequires -r


%build
%pyproject_wheel
%pyproject_save_files %{srcname}


%install
%pyproject_install


%files -n %{name} -f %{pyproject_files}
%license LICENSE
%doc README.md


%changelog
* Fri Mar 24 2023 Jiri Kyjovsky <j1.kyjovsky@gmail.com>
- Initial package 0.1.0
