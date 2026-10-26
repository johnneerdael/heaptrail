# Download and install

HeapTrail is a single binary with no runtime dependencies. You do not need a JVM to
analyze a heap dump. You can get it three ways: a prebuilt binary, `cargo install`, or a
build from source.

## What you need

| For | You need |
|---|---|
| Analyzing a dump | Nothing but the `heaptrail` binary. |
| `cargo install` or a source build | Rust 1.88 or newer. HeapTrail uses edition 2024 and `let` chains. Run `rustup update` if the build fails on an older toolchain. |
| Capturing from Android (`android-capture`) or `--auto-mapping` | [`adb`](https://developer.android.com/tools/adb) on your `PATH`, and a device or emulator it can reach. |
| Capturing from a JVM | `jmap` or `jcmd` from a JDK on the machine that runs the process. See [JVM dumps](../capture/jvm.md). |

For best speed, use a machine with at least four cores. The parser reads, parses and
records on separate threads.

## Option 1: a prebuilt binary

Each [release](https://github.com/johnneerdael/heaptrail/releases/latest) attaches an
archive for six targets. Each archive holds one file: `heaptrail`, or `heaptrail.exe` on
Windows.

| Platform | Archive |
|---|---|
| macOS, Apple silicon | `heaptrail-aarch64-apple-darwin.tar.gz` |
| macOS, Intel | `heaptrail-x86_64-apple-darwin.tar.gz` |
| Linux, x86-64 | `heaptrail-x86_64-unknown-linux-gnu.tar.gz` |
| Linux, ARM64 | `heaptrail-aarch64-unknown-linux-gnu.tar.gz` |
| Windows, x86-64 | `heaptrail-x86_64-pc-windows-msvc.zip` |
| Windows, ARM64 | `heaptrail-aarch64-pc-windows-msvc.zip` |

=== "macOS"

    ```bash
    curl -LO https://github.com/johnneerdael/heaptrail/releases/latest/download/heaptrail-aarch64-apple-darwin.tar.gz
    tar -xzf heaptrail-aarch64-apple-darwin.tar.gz
    sudo mv heaptrail /usr/local/bin/
    ```

    Use the `x86_64-apple-darwin` archive on an Intel Mac. If macOS blocks a binary you
    downloaded in a browser, remove the quarantine flag with
    `xattr -d com.apple.quarantine heaptrail`.

=== "Linux"

    ```bash
    curl -LO https://github.com/johnneerdael/heaptrail/releases/latest/download/heaptrail-x86_64-unknown-linux-gnu.tar.gz
    tar -xzf heaptrail-x86_64-unknown-linux-gnu.tar.gz
    sudo mv heaptrail /usr/local/bin/
    ```

    Use the `aarch64-unknown-linux-gnu` archive on an ARM64 machine.

=== "Windows"

    ```powershell
    Invoke-WebRequest -Uri https://github.com/johnneerdael/heaptrail/releases/latest/download/heaptrail-x86_64-pc-windows-msvc.zip -OutFile heaptrail.zip
    Expand-Archive heaptrail.zip -DestinationPath .
    ```

    Move `heaptrail.exe` to a folder on your `PATH`, or run it from where you unpacked it.

## Option 2: cargo install

```bash
cargo install heaptrail
```

This downloads the crate from [crates.io](https://crates.io/crates/heaptrail), builds it
in release mode (a minute or two) and installs `heaptrail` into `~/.cargo/bin`
(`%USERPROFILE%\.cargo\bin` on Windows).

No Rust yet? Install it with [rustup](https://rustup.rs), then open a new terminal so
`cargo` is on your `PATH`.

=== "macOS and Linux"

    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    ```

=== "Windows"

    ```powershell
    Invoke-WebRequest -Uri https://win.rustup.rs/x86_64 -OutFile rustup-init.exe
    ./rustup-init.exe
    ```

## Option 3: build from source

Use this to try a change that is on `master` but not in a release.

```bash
cargo install --git https://github.com/johnneerdael/heaptrail --force
```

Or clone the repository and build it yourself. The binary lands in `target/release/`.

```bash
git clone https://github.com/johnneerdael/heaptrail
cd heaptrail
cargo build --release
./target/release/heaptrail --version
```

## Check the install

```bash
heaptrail --version
```

<!-- output: version.txt -->
```text
heaptrail 1.4.2
```

If your shell says `command not found` (or `'heaptrail' is not recognized` on Windows),
the folder that holds the binary is not on your `PATH`. See the next section.

## Put cargo's bin folder on your PATH

`cargo install` writes binaries to `~/.cargo/bin`. `rustup` usually adds that folder to
your `PATH`. If it did not, add it yourself, then open a new terminal.

=== "zsh"

    ```bash
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    ```

=== "bash"

    ```bash
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
    ```

=== "fish"

    ```fish
    fish_add_path ~/.cargo/bin
    ```

=== "PowerShell"

    ```powershell
    [Environment]::SetEnvironmentVariable(
      "PATH",
      "$env:PATH;$env:USERPROFILE\.cargo\bin",
      "User"
    )
    ```

## Upgrade and uninstall

To upgrade a `cargo` install, run it again with `--force`. To upgrade a prebuilt binary,
download the newer archive and replace the file. Then check the version.

```bash
cargo install heaptrail --force
heaptrail --version
```

To remove a `cargo` install, run `cargo uninstall heaptrail`. To remove a prebuilt
binary, delete the file.

!!! tip "Which version do you need?"
    Use 1.4.0 or newer for Android work. Version 1.4.0 cleans stale dumps off the device
    during `android-capture`, 1.3.1 waits for the device to finish writing the dump, and
    1.1.1 fixed a panic on modern Android dumps. [What's new](whats-new.md) lists every
    release.

HeapTrail began as a fork of [agourlay/hprof-slurp](https://github.com/agourlay/hprof-slurp). The summary-only
binaries from that project's releases predate HeapTrail and lack every mode in this guide, so install HeapTrail
from the sources above.

## Related

- [Your first triage](first-triage.md) puts the install to work on a real dump.
- [Capture a heap dump](../capture/index.md) if you need a file to analyze.
- [Install the Claude Code plugin](../automate/claude-code-plugin.md) to let an agent run `heaptrail` for you.
