# (tpg) workaround for debuginfo generation
%define _unpackaged_files_terminate_build 0

%define api %(echo %{version} |cut -d. -f1)
%define major %(echo %{version} |cut -d. -f2)
%define libname %mklibname %{name} %{api} %{major}
%define devname %mklibname %{name} %{api} -d
%define debug_package %nil

%define compiler %(if [ -h %{__cc} ]; then ls -l %{__cc} |awk '{ print $11; }'; else echo %{__cc} |cut -d/ -f4; fi)

# (tpg) optimize it a bit
%global optflags %{optflags} -O3 -fopenmp

# (tpg) enable PGO build
%bcond_without pgo

Summary:	Crypto library written in C++
Name:		botan
Version:	3.7.1
Release:	1
Group:		System/Libraries
License:	BSD
Url:		https://botan.randombit.net/
Source0:	http://botan.randombit.net/releases/Botan-%{version}.tar.xz
BuildRequires:	python
BuildRequires:	pkgconfig(bzip2)
BuildRequires:	pkgconfig(gmp)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	boost-devel
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

%description -n python-%{name}
Python module for %{name}.

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}
Obsoletes:	%{_lib}botan1.10-static-devel
Obsoletes:	%{mklibname botan 1.11 -d } < 2.3.0

%description -n %{devname}
This package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup -p1 -n Botan-%{version}

# Update permissions for debuginfo package
find . -name "*.c" -o -name "*.h" -o -name "*.cpp" |xargs chmod 0644

%build
# we have the necessary prerequisites, so enable optional modules
%define enable_modules bzip2,zlib,sqlite3,lzma

# fixme: maybe disable unix_procs, very slow.
%define disable_modules proc_walk,unix_procs

%if %{with pgo}
CFLAGS="%{optflags} -fprofile-generate" \
CXXFLAGS="%{optflags} -fprofile-generate" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{build_ldflags} -fprofile-generate" ./configure.py \
	--prefix=%{_prefix} \
	--libdir=%{_lib} \
	--cc=%compiler \
	--os=linux \
	--cpu=%{_arch} \
	--enable-modules=%{enable_modules} \
	--disable-modules=%{disable_modules}

%make_build

export LD_LIBRARY_PATH="$(pwd)"
./botan-test ||:

llvm-profdata merge --output=%{name}-llvm.profdata $(find . -name "*.profraw" -type f)
PROFDATA="$(realpath %{name}-llvm.profdata)"
rm -f *.profraw
make clean

CFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
CXXFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{build_ldflags} -fprofile-use=$PROFDATA" \
%endif
./configure.py \
	--prefix=%{_prefix} \
	--libdir=%{_lib} \
	--cc=%compiler \
	--os=linux \
	--cpu=%{_arch} \
	--enable-modules=%{enable_modules} \
	--disable-modules=%{disable_modules}

%make_build

%install
%make_install DESTDIR="%{buildroot}"

rm -f %{buildroot}%{_libdir}/*.a

%check
%ifnarch %{ix86}
export LD_LIBRARY_PATH="$(pwd)"
./botan-test ||:
%endif

%files -n %{libname}
%{_libdir}/libbotan-%{api}.so.%{major}*

%files -n %{devname}
%{_bindir}/botan
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%{_libdir}/cmake/Botan-%{version}
%doc %{_docdir}/%{name}-%{version}/handbook
%doc %{_docdir}/%{name}-%{version}/*.txt
%doc %{_mandir}/man1/*.1*

%files -n python-%{name}
%{python_sitearch}/botan3.py
