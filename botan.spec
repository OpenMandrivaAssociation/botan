%define api 3
%define libname %mklibname botan
%define devname %mklibname -d botan

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
Obsoletes:	%{mklibname botan 3} < %{EVRD}
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
%rename %{mklibname botan 3 -d}
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

# botan-test spends most of its time on invalid inputs and rarely used
# algorithms; train on the CLI speed suite for common production paths.
# Extra ChaCha20Poly1305 / RSA-sign loops: a 64-byte-heavy mix and RSA
# keygen otherwise dominate the profile and regress those two paths.
%pgo
export LD_LIBRARY_PATH="$PWD/_OMV_rpm_build${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
_b=./_OMV_rpm_build/botan
$_b speed --msec=200 --buf-size=64,1024,1500,16384 --ecc-groups=secp256r1,secp384r1 \
	AES-128/GCM AES-256/GCM ChaCha20Poly1305 \
	SHA-256 SHA-384 SHA-512 SHA-3 \
	'HMAC(SHA-256)' \
	ChaCha AES-256 \
	X25519 ECDH ECDSA RSA \
	ML-KEM ML-DSA
$_b speed --msec=600 --buf-size=1024,4096 ChaCha20Poly1305
PYTHONPATH="$PWD/src/python${PYTHONPATH:+:$PYTHONPATH}" python - <<'PY'
import os
import time
import botan3 as botan

rng = botan.RandomNumberGenerator()
sk = botan.PrivateKey.create("rsa", 2048, rng)
signer = botan.PKSign(sk, "PKCS1v15(SHA-256)")
msg = os.urandom(48)
end = time.monotonic() + 8
while time.monotonic() < end:
	signer.update(msg)
	signer.finish(rng)

pt = os.urandom(1024)
enc = botan.SymmetricCipher("ChaCha20Poly1305", True)
enc.set_key(os.urandom(32))
end = time.monotonic() + 4
while time.monotonic() < end:
	enc.start(os.urandom(12))
	enc.finish(pt)
PY

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
