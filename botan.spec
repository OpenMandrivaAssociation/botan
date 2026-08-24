%define api 3
%define libname %mklibname %{name} %{api}
%define devname %mklibname %{name} %{api} -d

Summary:	Crypto library written in C++
Name:		botan
Version:	3.13.0
Release:	1
Group:		System/Libraries
License:	BSD
URL:		https://botan.randombit.net/
Source0:	https://botan.randombit.net/releases/Botan-%{version}.tar.xz
BuildRequires:	make
BuildRequires:	python
BuildRequires:	pkgconfig(bzip2)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(liblzma)
# For man page (rst2man)
BuildRequires:	python-docutils

%description
Botan is a BSD-licensed crypto library written in C++. It provides a
wide variety of basic cryptographic algorithms, X.509 certificates and
CRLs, PKCS \#10 certificate requests, a filter/pipe message processing
system, and a wide variety of other features, all written in portable
C++. The API reference, tutorial, and examples may help impart the
flavor of the library.

%package -n %{libname}
Summary:	Main library for %{name}
Group:		System/Libraries
Provides:	%{name} = %{EVRD}
Obsoletes:	%{mklibname botan 3 12} < %{EVRD}
Obsoletes:	%{mklibname botan 1.11 21} < 2.3.0
Obsoletes:	%{mklibname botan 1.11 30} < 2.3.0

%description -n %{libname}
Botan is a BSD-licensed crypto library written in C++. It provides a
wide variety of basic cryptographic algorithms, X.509 certificates and
CRLs, PKCS \#10 certificate requests, a filter/pipe message processing
system, and a wide variety of other features, all written in portable
C++. The API reference, tutorial, and examples may help impart the
flavor of the library.

%package -n python-%{name}
Summary:	Python lib for %{name}
Group:		Development/Python
Requires:	%{libname} = %{EVRD}

%description -n python-%{name}
Python module for %{name}.

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}
Obsoletes:	%{_lib}botan1.10-static-devel
Obsoletes:	%{mklibname botan 1.11 -d} < 2.3.0

%description -n %{devname}
This package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup -p1 -n Botan-%{version}

%conf
%set_build_flags
python ./configure.py \
	--prefix=%{_prefix} \
	--libdir=%{_lib} \
	--os=linux \
	--cpu=%{_arch} \
	--with-build-dir=_OMV_rpm_build \
	--with-bzip2 \
	--with-zlib \
	--with-sqlite3 \
	--with-lzma \
	--disable-static-library \
	--without-sphinx \
	--with-rst2man \
	--distribution-info="OpenMandriva %{EVRD}"

%build
%make_build -f _OMV_rpm_build/Makefile

%install
%make_install -f _OMV_rpm_build/Makefile
# remove doc build leftovers
rm -rf %{buildroot}%{_docdir}/%{name}-%{version}/handbook/.{buildinfo,doctrees}

%pgo
export LD_LIBRARY_PATH="$PWD/_OMV_rpm_build${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
./_OMV_rpm_build/botan-test

%if ! %{cross_compiling}
%check
%ifnarch %{ix86}
export LD_LIBRARY_PATH="$PWD/_OMV_rpm_build${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
./_OMV_rpm_build/botan-test
%endif
%endif

%files -n %{libname}
%license license.txt
%{_libdir}/libbotan-%{api}.so.*

%files -n %{devname}
%{_bindir}/botan
%{_includedir}/botan-%{api}
%{_libdir}/libbotan-%{api}.so
%{_libdir}/pkgconfig/botan-%{api}.pc
%{_libdir}/cmake/Botan-%{version}
%doc %{_docdir}/%{name}-%{version}/handbook
%doc %{_docdir}/%{name}-%{version}/*.txt
%{_mandir}/man1/botan.1*

%files -n python-%{name}
%{python_sitearch}/botan3.py
%{python_sitearch}/__pycache__/botan3.*
