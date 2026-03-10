# SubtitleFinder – DaVinci Resolve Plugin

Search and navigate subtitle tracks directly inside DaVinci Resolve.  
Works on **both the free and paid (Studio) versions**.

---

## How it appears inside Resolve

After installation the script shows up under:

```
Workspace  ▸  Scripts  ▸  Edit  ▸  SubtitleFinder
```

Click it to open the search window.

> **Note – "Workflow Integrations" is different.**  
> `Workspace > Workflow Integrations` is a paid-Studio-only feature and is
> greyed out in the free version. This plugin does **not** use Workflow
> Integrations — it uses the `Scripts` menu, which is available to everyone.

---

## Requirements

| Requirement | Details |
|---|---|
| DaVinci Resolve | 17 or later (free or Studio) |
| Python | 3.8 or newer (64-bit) |
| OS | macOS, Windows, Linux |

---

## Installation

### Option A – Automatic (recommended)

Run `install.py` from a terminal. No admin/sudo required on any platform.

**macOS / Linux**
```bash
python3 install.py
```

**Windows**
```
python install.py
```

Then **restart DaVinci Resolve**.

---

### Option B – Manual (copy the file yourself)

Copy `SubtitleFinder/subtitle-search.py` into the **Scripts/Edit** folder
for your OS, renaming it `SubtitleFinder.py`:

| OS | Folder |
|---|---|
| macOS | `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Edit/` |
| Windows | `%APPDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Edit\` |
| Linux | `~/.local/share/DaVinciResolve/Fusion/Scripts/Edit/` |

Then restart DaVinci Resolve. The script appears under `Workspace > Scripts`.

---

## One-time setup for the FREE version

The free version of DaVinci Resolve restricts which scripts can connect to
its API. You need to change one Preferences setting **once**:

1. Open **DaVinci Resolve > Preferences** (macOS) or **File > Preferences** (Windows/Linux).
2. Go to **System → General**.
3. Find **"External scripting using"** and change it from `None` to **`Local`**.
4. Click **Save** and restart Resolve.

After that, the script will connect normally.

> **Studio (paid) users** do not need to change this setting — it works out
> of the box.

---

## Usage

1. Open a project and switch to the **Edit** page.
2. Go to **Workspace > Scripts > Edit > SubtitleFinder**.
3. In the search window:
   - Type a word or phrase and press **Enter** or click **Find Occurrences**.
   - Toggle **Match Case**, **Whole Word**, or **Regular Expression** as needed.
   - Change **Subtitle Track** if your subtitles are not on track 1.
   - Click any row to jump the playhead to that subtitle.

---

## Uninstall

```bash
python3 install.py --uninstall
```

Or manually delete `SubtitleFinder.py` from the Scripts/Edit folder listed above.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Script doesn't appear in the menu | Restart Resolve after installing |
| "resolve object is None" error (free version) | Enable **Local** scripting in Preferences (see above) |
| "DaVinciResolveScript not found" | Make sure Resolve is **open** before running the script |
| No subtitles listed | Check the **Subtitle Track** number in the UI — it defaults to 1 |
| Linux – script not found | Try the system path `/opt/resolve/Fusion/Scripts/Edit/` instead |

---

## Folder Structure

```
SubtitleFinder-Plugin/
├── install.py                  ← Run this to install / uninstall
├── README.md
└── SubtitleFinder/
    └── subtitle-search.py      ← The actual plugin script
```
