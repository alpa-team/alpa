%global srcname alpa-conf


Name:           python-%{srcname}
Version:        0.2.1
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
%autosetup -p1 -n alpa_conf-%{version}


%generate_buildrequires
%pyproject_buildrequires -r


%build
%pyproject_wheel


%install
%pyproject_install
# For official Fedora packages, including files with '*' +auto is not allowed
# Replace it with a list of relevant Python modules/globs and list extra files in %%files
%pyproject_save_files alpa_conf


%check
%pyproject_check_import


%files -n python3-%{srcname} -f %{pyproject_files}
%license LICENSE
%doc README.md


%changelog
* Fri Mar 24 2023 Jiri Kyjovsky <j1.kyjovsky@gmail.com> - 0.1.0-1
- Initial package
