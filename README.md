# caelestia-shell for fedora

Fedora RPM packaging for the [Caelestia desktop shell](https://github.com/caelestia-dots/shell).

## Prerequisites

caelestia-shell requires `quickshell-git`, which is available from a separate COPR:

```sh
sudo dnf copr enable errornointernet/quickshell
sudo dnf install quickshell-git
```

## Installing from COPR

Enable the repository and install:

```sh
sudo dnf copr enable celestelove/caelestia-shell
sudo dnf install caelestia-shell
```

## Building from source

Install the build dependencies:

```sh
sudo dnf install rpm-build cmake ninja-build gcc-c++ \
    qt6-qtbase-devel qt6-qtdeclarative-devel libqalculate-devel \
    aubio-devel pipewire-devel libcava-devel
```

Download the source tarball into your rpmbuild sources directory, then build:

```sh
spectool -g -R caelestia.spec
rpmbuild -ba caelestia.spec
```

The resulting RPM will be in `~/rpmbuild/RPMS/x86_64/`.

## License

This packaging spec is licensed under MIT. The upstream Caelestia shell is licensed under [GPL-3.0-only](https://github.com/caelestia-dots/shell/blob/main/LICENSE).
