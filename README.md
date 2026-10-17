# Juice Goose KIN-1000 for Q-SYS

Control and monitor a Juice Goose KIN-1000 UPS using its binary RS-232 interface. Includes load/battery levels, input/output voltage and frequency, AVR/overload/fault/battery/test-mode status, self-test, AC-normal-restart, wake-up timer and pre-shutdown countdown.

Plugin and package version: **1.0.0.26**.

Version 1.0.0.26 has **Setup** and **Controls** pages, with the existing logo,
white canvas, gray panels, aligned fields, native group captions and version
footers. Setup holds serial configuration and connection status; Controls holds
commands, scheduling, readings and indicators. Existing identity, all control/pin
bindings and momentary button behavior are preserved. Serial/UPS behavior is
unchanged; Function Calls is now a separate debug choice.

For manual source installation, copy only `content/JuiceGooseKin1000ApRmUps.qplug`
into Designer's Plugins folder after backing up the previous file elsewhere.
Designer and hardware acceptance remain deferred; see the
[source review](docs/SDK-REVIEW-1.0.0.26.md).

## Install with Q-SYS Library

1. Sign in to [Q-SYS Library](https://library.qsys.com/my-library).
2. Open **My Packages → Add Personal Package**.
3. Enter **Juice Goose KIN-1000** and this package URL:

   ```text
   https://joshua-small.github.io/qsys-juicegoose-kin1000/registration/joshuasmall.qsys.juicegoosekin1000/index.json
   ```

4. In Designer, sign in with the same QSC ID and open **Tools → Show Asset Installer**.
5. Refresh **Available Assets**, select the package and install it.

For manual installation, download `JuiceGooseKin1000ApRmUps.qplug` from [Releases](https://github.com/joshua-small/qsys-juicegoose-kin1000/releases) and place only that file in your Documents folder under `QSC/Q-Sys Designer/Plugins`. Keep backups and support files outside Plugins. Use one installation method to avoid duplicate copies. Refreshing/installing a package does not deploy changes to a Core; update and test the design before **Save to Core & Run**.

## Connect and operate

1. Add **Juice Goose > KIN-1000** to a test design.
2. Connect a Q-SYS Serial Port component to **Serial Port**. The plugin opens it at **1200 baud, 8N1**.
3. Run the design and check the status readouts. Polling defaults to 5 seconds and can be set from 2 to 60 seconds.
4. Confirm telemetry before enabling automation. Self-test, restart, wake and countdown controls send commands without a documented acknowledgement.

## Protocol limits

Load and battery are raw byte levels, not established percentages. Voltage/frequency units are inferred from the protocol. The source document's serial word-length wording is ambiguous; 8N1 is the implementation assumption. Verify cabling and any DTR/RTS requirement with the actual UPS. Only the status poll has a documented 16-byte response, so a command write does not prove execution.

Targets Q-SYS Designer/Core 10.5. Offline status checks cover all 128 flag combinations; physical UPS operation and native Designer rendering remain unverified. Verify shutdown-related controls under safe commissioning conditions before use.

## Offline validation

From the repository root:

```sh
uv run --no-project --with lupa python tests/test_candidate.py
uv run --no-project python scripts/verify.py
dotnet pack JuiceGooseKin1000.csproj -o dist
```

The tests include a preserved 1.0.0.25 source fixture for compatibility checks and
a standalone offline layout checker. They cover 72 page/property combinations,
negative layout mutations, declarations/pins, command bytes and 128 status flag
combinations. Test files are excluded from the package and must not be installed
in Designer's Plugins folder. These mocks do not establish native rendering or
UPS acceptance.

## Support

Report bugs through [Issues](https://github.com/joshua-small/qsys-juicegoose-kin1000/issues), including plugin version, Q-SYS version, device/broker model and firmware, and reproduction steps. Remove credentials from logs and design files before sharing them.

This is an independent personal package, not a Q-SYS Verified Asset or a manufacturer-endorsed release. Manufacturer names and logos identify compatible products. Existing source attribution is retained.
