# Juice Goose KIN-1000 1.0.0.26 layout review

Reviewed source SHA-256: `d704f5034a2621256f2f63dce93bc5988e965c945852999f195b04231a51f71a`.
Baseline 1.0.0.25: `06553de7ae9c8bcbc6bc2e1d0918ab3159ffe7a0675267e1ca3931c357daa407`.
Target: Designer/Core 10.5. Official Developer Help is current, unversioned guidance.

## Requirements and implementation

| Requirement / convention | Evidence |
| --- | --- |
| [Reserved Functions](https://help.qsys.com/DeveloperHelp/Content/Standards_Definitions/Reserved_Functions.htm): page order, layout names, geometry, controls and pins are SDK contracts | GetPages returns Setup, Controls; dispatch selects the corresponding named page function. All 29 declarations, scalar counts, internal names, serial pin and PrettyNames match baseline. Hidden placeholders retain bindings on the other page. |
| Shared ZOrder is documented; assigning every object's order follows QSC recommendation. Distinct values are the house convention | Each page has unique graphics/control orders, with containing panels behind their contents. Graphics start at 1; controls start at 1000. Negative fixtures reject duplicate orders and missing captions. |
| House composition, dimensions and palettes | Setup is 400 x 440; Controls is 400 x 846. Both have a white canvas, gray 400 x 80 brand panel, left-aligned 20-point title at (7,86), gray content panel at (5,110), native Header captions and lower-right 10-point version footer. Labels use black, normally 13 point. Serial/readout rows have label and field columns at x=30/180 or 20/180, 25-pixel pitch. |
| Logo preservation | The unchanged embedded SVG has viewBox 1126.8037013249 x 173.1105770255. Both pages center it at x=12.5, y=11.1944 with size 375 x 57.6112, preserving its proportions. No new logo or brand color was inferred. |
| Setup content | KIN-1000 Serial Connection and Connection Status groups; serial values reflect existing Open(1200,8,"N",1). The port remains assigned through the schematic pin. Static configuration fields are graphics, avoiding new control contracts or false editable settings. |
| Controls content | Commands, Scheduling, Readings and Status groups; 45 x 20 native white command buttons, 25-pixel rows, readable fields, and two aligned columns of 16 x 16 LEDs. Scheduling labels explicitly identify pre-shutdown minutes/seconds. |
| Optional native color overrides | No TextColor, OffColor or UnlinkOffColor. Named palette constants replace repeated literals. Positive/fault/warning/mode meanings from the previous status correction remain unchanged. |
| Momentary compatibility exception | Existing Momentary declarations and button styles are preserved intentionally, rather than converting them to the house default Trigger. Press/release behavior and pins remain identical. Set legends distinguish the two scheduling actions. |
| [Code Style](https://help.qsys.com/DeveloperHelp/Content/Standards_Definitions/Style_Guide.htm): recommended naming/source organization | Expanded direct SDK layout tables, named Setup/Controls functions, visible definitions ordered by group, hidden placeholders in control declaration order. No generic layout framework runs in the plugin. Debug choices now include Function Calls. |
| [Serial practices](https://help.qsys.com/DeveloperHelp/Content/Recommended_Practices/Serial.htm) and [Lua Scopes](https://help.qsys.com/DeveloperHelp/Content/Recommended_Practices/LuaScoping.htm): affected runtime boundary | Entire runtime body is byte-for-byte text-equivalent after normalizing the added Function Calls debug selection. Serial setup, protected opening, global host objects/timers, queue, callbacks, framing and status logic are unchanged. |

## Validation

- 72 page/property variants pass geometry, containment, label, stacking, footer,
  binding, logo and optional-color checks. Poll intervals 2/5/60, six debug choices
  and debug visibility on/off cover all layout-relevant configurations.
- Missing-caption and duplicate-order mutations are rejected.
- Identity, all 29 controls, pin contract, PrettyNames and poll property preserved.
- Full Lua runtime mocks compare startup serial settings and outgoing command
  bytes across property/value variants; release events send no duplicate commands.
- 128 status-flag combinations retain severity precedence, recovery and aggregate
  LED truth table.
- LuaLS 3.19.1, Information level, zero diagnostics; no categories disabled.
  The successful run's command/exit/output is retained in local diagnostic evidence.
- A fresh independent reviewer retrieved applicable official requirements,
  inspected the final source and diagnostic output, and independently reran the
  final regression suite. No blocking SDK source-review finding remains.

## Limits

No Computer Use, Designer rendering/load/save-reopen, Core or UPS operation was
performed. Native off/text colors, clipping, selected/deselected appearance and
dragged graphics over black still need Designer acceptance. Protocol uncertainties
inherited from 1.0.0.25 remain unchanged. These checks do not establish Q-SYS
Library acceptance or manufacturer endorsement.

Application and device acceptance remain pending.
