Summary of what we did

  Problem

  HiBig Zero e-reader app on Bigme HiBreak B6 showed 6.8 mA idle drain (29 mAh overnight) — should be near zero for an e-ink device.

  6 bugs found and fixed

  ┌─────┬──────────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────┬───────────────────┐
  │ Bug │                                   What                                   │                            Fix                            │      Impact       │
  ├─────┼──────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────┤
  │ 1   │ Config "\\n" written as literal backslash+n, all settings lost on reload │ Changed to "\n" in ConfigManager.java                     │ 0 mA (indirect)   │
  ├─────┼──────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────┤
  │ 2   │ Auto-shutdown daemon dies when su shell exits (cgroup teardown)          │ Daemon v2.2 with cgroup escape + setsid + PID file check  │ ~4.0 mAh          │
  ├─────┼──────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────┤
  │ 3   │ writeBootTime uses non-root exec, can't write to /data/local/tmp         │ Changed to execRoot                                       │ 0 mA (diagnostic) │
  ├─────┼──────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────┤
  │ 4   │ uart2serport crash loop wakes CPU every 5s (init counts exit as crash)   │ exec sleep 2147483647 stub + SELinux rule + Magisk module │ ~21.4 mAh (74%)   │
  ├─────┼──────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────┤
  │ 5   │ appendLog memory-only                                                    │ Skipped — diagnostic only, not a drain source             │ —                 │
  ├─────┼──────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────┼───────────────────┤
  │ 6   │ Deep doze never engaged (30-min floor)                                   │ Self-resolves after Bug 4 fix                             │ consequence       │
  └─────┴──────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────┴───────────────────┘

  Files modified

  - ConfigManager.java — newline fix
  - BootReceiver.java — uart passive monitor, daemon PID file check, writeBootTime root
  - assets/auto_shutdown.sh — v2.2 daemon with cgroup escape, single-instance guard
  - modules/uart_fix/ — 6 files: Magisk module with SELinux rule, service.sh, daemon copy
  - AndroidManifest.xml — version bump 1.0.0 → 1.1.0
  - MainActivity.java — version string in UI
  - build.py — version strings

  Deployed & verified on device

  - APK built and installed (v1.1.0)
  - Daemon running at PID 5140, parented to init (survives shell exit)
  - Config file now has proper newlines
  - UART service running stable (no more crash loop)

  Created

  - docs/DRAIN_REPORT_2026-09-14.md — updated with all fixes
  - docs/OPTIMIZATIONS_2026-09-14.md — 7 new optimization suggestions (was about to start implementing #1 when we paused)

  What's left

  - 7 additional optimizations identified (CPU scaling, vendor app restriction, alarm suppression, etc.)
  - Overnight test to confirm the drain improvement
  ╰─ Interrupted · What should Tau do instead?