%define myname botan
%define api 1.8.2
%define libname %mklibname %{myname} %{api}
%define develname %mklibname %{myname} -d
%define staticname %mklibname %{myname} -s -d

Name:           %{myname}
Version:        1.8.13
Release:        %mkrel 2
Summary:        Crypto library written in C++

Group:          System/Libraries
License:        BSD
URL:            http://botan.randombit.net/
# tarfile is stripped using repack.sh. original tarfile to be found
# here: http://files.randombit.net/botan/Botan-%%{version}.tbz
Source0:        Botan-%{version}.stripped.tbz
Source1:        README.fedora
# soname was changed unintentionally upstream, revert it.
Patch0:         botan-1.8.13-soname.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires:  gcc-c++
BuildRequires:  python

BuildRequires:  bzip2-devel
BuildRequires:  zlib-devel
BuildRequires:  gmp-devel
BuildRequires:  openssl-devel


%description
Botan is a BSD-licensed crypto library written in C++. It provides a
wide variety of basic cryptographic algorithms, X.509 certificates and
CRLs, PKCS \#10 certificate requests, a filter/pipe message processing
system, and a wide variety of other features, all written in portable
C++. The API reference, tutorial, and examples may help impart the
flavor of the library.

%package -n     %{libname}

#(!) summary for main lib RPM only
Summary:        Main library for %{myname}
Group:          System/Libraries
Provides:       %{name} = %{version}-%{release}

%description -n %{libname}
Botan is a BSD-licensed crypto library written in C++. It provides a
wide variety of basic cryptographic algorithms, X.509 certificates and
CRLs, PKCS \#10 certificate requests, a filter/pipe message processing
system, and a wide variety of other features, all written in portable
C++. The API reference, tutorial, and examples may help impart the
flavor of the library.

%package        -n %{develname}
Summary:        Development files for %{name}
Group:          Development/Other
Requires:       %{libname} = %{version}
Requires:       pkgconfig
Requires:       bzip2-devel
Requires:       zlib-devel
Requires:       gmp-devel
Requires:       openssl-devel
Provides:       %{name}-devel = %{version}-%{release}

%description    -n %{develname}
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package -n %{staticname}
Summary:        Static libraries for %{name}
Group:          Development/Other
Requires:       %{name}-devel = %{version}-%{release}

%description  -n %{staticname}
The %{staticname} package contains the static libraries
of %{name}.

%prep
%setup -q -n Botan-%{version}
%patch0 -p0
cp -av %{SOURCE1} .

%build
# we have the necessary prerequisites, so enable optional modules
%define enable_modules gnump,bzip2,zlib,openssl

# fixme: maybe disable unix_procs, very slow.
%define disable_modules %{nil}

./configure.py \
        --prefix=%{_prefix} \
        --libdir=%{_lib} \
        --cc=gcc \
        --os=linux \
        --cpu=%{_arch} \
        --enable-modules=%{enable_modules} \
        --disable-modules=%{disable_modules}

# (ab)using CXX as an easy way to inject our CXXFLAGS
make CXX="g++ ${CXXFLAGS:-%{optflags}}" %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install \
     DESTDIR=%{buildroot}%{_prefix} \
     DOCDIR=_doc \
     INSTALL_CMD_EXEC="install -p -m 755" \
     INSTALL_CMD_DATA="install -p -m 644" \


%clean
rm -rf %{buildroot}


%post -p /sbin/ldconfig


%postun -p /sbin/ldconfig


%files -n %{libname}
%defattr(-,root,root,-)
%{_libdir}/libbotan*-*.so
%doc _doc/readme.txt _doc/log.txt _doc/thanks.txt _doc/credits.txt 
%doc _doc/license.txt _doc/fips140.tex _doc/pgpkeys.asc
%doc README.fedora


%files -n %{develname}
%defattr(-,root,root,-)
%doc doc/examples
%doc _doc/api* _doc/tutorial*
%{_bindir}/botan-config
%{_includedir}/*
%exclude %{_libdir}/libbotan.a
%{_libdir}/libbotan.so
%{_libdir}/pkgconfig/botan-1.8.pc

%files -n %{staticname}
%defattr(-,root,root)
%attr(0644,root,root) %{_libdir}/lib*.a

%check
make CXX="g++ ${CXXFLAGS:-%{optflags}}" %{?_smp_mflags} check

# these checks would fail
mv checks/validate.dat{,.orig}
awk '/\[.*\]/{f=0} /\[(RC5.*|RC6|IDEA)\]/{f=1} (f && !/^#/){sub(/^/,"#")} {print}' \
    checks/validate.dat.orig > checks/validate.dat
LD_LIBRARY_PATH=%{buildroot}%{_libdir} ./check --validate




%changelog
* Fri Aug 12 2011 Shlomi Fish <shlomif@mandriva.org> 1.8.13-2mdv2012.0
+ Revision: 694224
- import botan

