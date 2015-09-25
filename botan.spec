%define	api 1.10
%define	major 0
%define libname %mklibname %{name} %{api} %{major}
%define devname %mklibname %{name} %{api} -d

%define compiler %(echo %{__cc} |cut -d/ -f4)

Summary:        Crypto library written in C++
Name:           botan
Version:        1.11.20
Release:        1
Group:          System/Libraries
License:        BSD
Url:            http://botan.randombit.net/
Source0:        http://botan.randombit.net/releases/Botan-%{version}.tgz
Patch0:		botan-aarch64.patch
Patch1:		botan-1.11.20-build-python.patch
# Much better suited for crosscompiles

BuildRequires:  python
BuildRequires:  bzip2-devel
BuildRequires:  gmp-devel
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  boost-devel

%description
Botan is a BSD-licensed crypto library written in C++. It provides a
wide variety of basic cryptographic algorithms, X.509 certificates and
CRLs, PKCS \#10 certificate requests, a filter/pipe message processing
system, and a wide variety of other features, all written in portable
C++. The API reference, tutorial, and examples may help impart the
flavor of the library.

%package -n	%{libname}
Summary:	Main library for %{name}
Group:		System/Libraries
Provides:	%{name} = %{version}-%{release}

%description -n	%{libname}
Botan is a BSD-licensed crypto library written in C++. It provides a
wide variety of basic cryptographic algorithms, X.509 certificates and
CRLs, PKCS \#10 certificate requests, a filter/pipe message processing
system, and a wide variety of other features, all written in portable
C++. The API reference, tutorial, and examples may help impart the
flavor of the library.

%package -n	%{devname}
Summary:	Development files for %{name}
Group:		Development/Other
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{_lib}botan1.10-static-devel

%description -n	%{devname}
This package contains libraries and header files for
developing applications that use %{name}.

%prep
%setup -qn Botan-%{version}
%apply_patches

# Update permissions for debuginfo package
find . -name "*.c" -o -name "*.h" -o -name "*.cpp" |xargs chmod 0644

mkdir pybin
ln -s %{_bindir}/python2 pybin/python
export PATH=`pwd`/pybin:$PATH

%build
# we have the necessary prerequisites, so enable optional modules
%define enable_modules bzip2,zlib,openssl,sqlite3

# fixme: maybe disable unix_procs, very slow.
%define disable_modules proc_walk,unix_procs

./configure.py \
        --prefix=%{_prefix} \
        --libdir=%{_lib} \
        --cc=%compiler \
        --os=linux \
        --cpu=%{_arch} \
        --enable-modules=%{enable_modules} \
        --disable-modules=%{disable_modules}

%make CXX="%{__cxx} -pthread" AR="%{__ar} crs" LIB_OPT="-c %{optflags}"

%install
make install \
	DESTDIR=%{buildroot}%{_prefix} \
	DOCDIR=_doc \
	INSTALL_CMD_EXEC="install -p -m 755" \
	INSTALL_CMD_DATA="install -p -m 644" \

rm -f %{buildroot}%{_libdir}/*.a

%check
%make check

%files -n %{libname}
%{_libdir}/libbotan-%{api}.so.%{major}*

%files -n %{devname}
%{_includedir}/*
%{_bindir}/botan-config-%{api}
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
