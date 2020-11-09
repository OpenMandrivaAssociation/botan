%define api %(echo %{version} |cut -d. -f1)
%define major %(echo %{version} |cut -d. -f2)
#define major 17
%define libname %mklibname %{name} %{api} %{major}
%define devname %mklibname %{name} %{api} -d
%define debug_package %nil

%define compiler %(echo %{__cc} |cut -d/ -f4)

# (tpg) optimize it a bit
%global optflags %{optflags} -Ofast -fopenmp

# (tpg) enable PGO build
%ifnarch %{ix86} riscv64
%bcond_without pgo
%else
%bcond_with pgo
%endif

Summary:	Crypto library written in C++
Name:		botan
Version:	2.17.1
Release:	1
Group:		System/Libraries
License:	BSD
Url:		http://botan.randombit.net/
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
%define enable_modules bzip2,zlib,openssl,sqlite3,lzma

# fixme: maybe disable unix_procs, very slow.
%define disable_modules proc_walk,unix_procs

%if %{with pgo}
export LD_LIBRARY_PATH="$(pwd)"
export LLVM_PROFILE_FILE=%{name}-%p.profile.d
CFLAGS="%{optflags} -fprofile-instr-generate" \
CXXFLAGS="%{optflags} -fprofile-instr-generate" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{ldflags} -fprofile-instr-generate" ./configure.py \
	--prefix=%{_prefix} \
	--libdir=%{_lib} \
	--cc=%compiler \
	--os=linux \
	--cpu=%{_arch} \
	--with-openmp \
	--enable-modules=%{enable_modules} \
	--disable-modules=%{disable_modules}

%make_build

./botan-test ||:

unset LD_LIBRARY_PATH
unset LLVM_PROFILE_FILE
llvm-profdata merge --output=%{name}.profile $(find . -type f -name "*.profile.d")
rm -f *.profile.d
make clean

CFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
CXXFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{ldflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
%endif
./configure.py \
	--prefix=%{_prefix} \
	--libdir=%{_lib} \
	--cc=%compiler \
	--os=linux \
	--cpu=%{_arch} \
	--with-openmp \
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
%{_docdir}/%{name}-%{version}/handbook
%{_docdir}/%{name}-%{version}/*.txt
%{_mandir}/man1/*.1*

%files -n python-%{name}
%{python_sitearch}/botan2.py
%{python_sitearch}/__pycache__/*
