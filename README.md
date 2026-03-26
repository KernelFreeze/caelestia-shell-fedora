# caelestia for fedora

Fedora RPM packaging for the [Caelestia desktop shell](https://github.com/caelestia-dots/shell) and [CLI](https://github.com/caelestia-dots/cli).

## Prerequisites

caelestia-shell requires `quickshell-git`, `libcava`, `gpu-screen-recorder`, and `app2unit`, each available from separate COPRs:

```sh
sudo dnf copr enable errornointernet/quickshell
sudo dnf install quickshell-git
```

```sh
sudo dnf copr enable celestelove/libcava
sudo dnf install libcava-devel
```

```sh
sudo dnf copr enable celestelove/app2unit
sudo dnf install app2unit
```

```sh
sudo dnf copr enable brycensranch/gpu-screen-recorder-git
sudo dnf install gpu-screen-recorder-ui
```

## Installing from COPR

Enable the repository and install:

```sh
sudo dnf copr enable celestelove/caelestia
sudo dnf install caelestia-shell caelestia-cli
```

## Building from source

### caelestia-shell

Install the build dependencies:

```sh
sudo dnf install rpm-build cmake ninja-build gcc-c++ \
    qt6-qtbase-devel qt6-qtdeclarative-devel libqalculate-devel \
    aubio-devel pipewire-devel libcava-devel
```

Download the source tarball and build:

```sh
spectool -g -R caelestia-shell.spec
rpmbuild -ba caelestia-shell.spec
```

The resulting RPM will be in `~/rpmbuild/RPMS/x86_64/`.

### caelestia-cli

Install the build dependencies:

```sh
sudo dnf install rpm-build python3-devel python3-build \
    python3-installer python3-hatchling python3-hatch-vcs
```

Download the source tarball and build:

```sh
spectool -g -R caelestia-cli.spec
rpmbuild -ba caelestia-cli.spec
```

The resulting RPM will be in `~/rpmbuild/RPMS/noarch/`.

## License

These packaging specs are licensed under MIT. The upstream Caelestia projects are licensed under [GPL-3.0-only](https://github.com/caelestia-dots/shell/blob/main/LICENSE).
