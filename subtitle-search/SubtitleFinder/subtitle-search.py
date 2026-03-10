"""
SubtitleFinder – subtitle-search.py
Launched via  Workspace > Scripts  inside DaVinci Resolve.

Works on both DaVinci Resolve (free) and DaVinci Resolve Studio (paid).
"""

import sys
import os
import re

# ── Resolve API bootstrap ──────────────────────────────────────────────────────
# When run from  Workspace > Scripts, Resolve injects the global variables
#   resolve, fusion, bmd, ui (and app on some versions).
# When run externally (e.g. from a terminal) we must import the module manually.

def _bootstrap_resolve():
    """Return (resolve, bmd) however we can."""

    # 1. Already injected by Resolve's script runner (free + paid, menu launch)
    _globals = sys._getframe(1).f_globals  # caller's global scope … usually __main__
    injected_resolve = (
        globals().get("resolve")       # paid / newer free
        or globals().get("app") and globals()["app"].GetResolve()  # free fallback
    )
    if injected_resolve:
        _bmd = globals().get("bmd") or _load_dvr_script()
        return injected_resolve, _bmd

    # 2. External launch – load DaVinciResolveScript manually
    dvr = _load_dvr_script()
    if dvr is None:
        return None, None
    return dvr.scriptapp("Resolve"), dvr


def _load_dvr_script():
    """Try to import DaVinciResolveScript from the standard locations."""
    try:
        import DaVinciResolveScript as dvr
        return dvr
    except ImportError:
        pass

    paths = {
        "darwin": "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules",
        "win32":  os.path.expandvars(r"%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"),
        "linux":  "/opt/resolve/Developer/Scripting/Modules",
    }
    p = paths.get(sys.platform, "")
    if p and os.path.exists(p) and p not in sys.path:
        sys.path.append(p)
    try:
        import DaVinciResolveScript as dvr
        return dvr
    except ImportError:
        return None


# ── Timecode helpers ───────────────────────────────────────────────────────────

def frame_to_timecode(frames, frame_rate=24.0):
    fps = max(1, int(round(frame_rate)))
    ff  = int(frames % fps)
    total_sec = int(frames // fps)
    ss = total_sec % 60
    mm = (total_sec // 60) % 60
    hh = total_sec // 3600
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"


def build_pattern(search_term, match_case, whole_word, use_regex):
    flags = 0 if match_case else re.IGNORECASE
    pat   = search_term if use_regex else re.escape(search_term)
    if whole_word:
        pat = r'\b' + pat + r'\b'
    try:
        return re.compile(pat, flags)
    except re.error as e:
        print(f"Invalid regular expression: {e}")
        return None


# ── Main UI ────────────────────────────────────────────────────────────────────

def show_ui(resolve, bmd_module):
    fusion     = resolve.Fusion()
    ui         = fusion.UIManager
    dispatcher = bmd_module.UIDispatcher(ui)

    win_layout = ui.VGroup([
        ui.Label({
            "Text": "Subtitle Search",
            "Weight": 0,
            "Font": ui.Font({"PixelSize": 16, "Bold": True}),
            "Alignment": {"AlignHCenter": True},
        }),
        ui.VGap(8),
        ui.HGroup({"Weight": 0}, [
            ui.Label({"Text": "Search Text:", "Weight": 0.3}),
            ui.LineEdit({
                "ID": "SearchInput",
                "PlaceholderText": "Enter text to find…",
                "Weight": 0.7,
            }),
        ]),
        ui.HGroup({"Weight": 0}, [
            ui.Label({"Text": "", "Weight": 0.3}),
            ui.CheckBox({"ID": "MatchCase", "Text": "Match Case",         "Checked": False, "Weight": 0}),
            ui.HGap(8, 0),
            ui.CheckBox({"ID": "WholeWord", "Text": "Whole Word",         "Checked": True,  "Weight": 0}),
            ui.HGap(8, 0),
            ui.CheckBox({"ID": "UseRegex",  "Text": "Regular Expression", "Checked": False, "Weight": 0}),
            ui.Label({"Text": "", "Weight": 1}),
        ]),
        ui.HGroup({"Weight": 0}, [
            ui.Label({"Text": "Subtitle Track:", "Weight": 0.3}),
            ui.SpinBox({"ID": "TrackNum", "Minimum": 1, "Maximum": 99, "Value": 1, "Weight": 0.15}),
            ui.Label({"Text": "", "Weight": 0.55}),
        ]),
        ui.VGap(8),
        ui.Tree({"ID": "ResultsTree", "Weight": 1}),
        ui.VGap(4),
        ui.Label({"ID": "StatusLabel", "Text": "Ready.", "Weight": 0}),
        ui.VGap(6),
        ui.HGroup({"Weight": 0}, [
            ui.Button({"ID": "FindBtn",   "Text": "Find Occurrences"}),
            ui.Button({"ID": "CancelBtn", "Text": "Close"}),
        ]),
    ])

    win = dispatcher.AddWindow({
        "ID":          "SubtitleSearchWin",
        "Geometry":    [200, 200, 700, 480],
        "WindowTitle": "SubtitleFinder",
    }, win_layout)

    items = win.GetItems()

    tree = items["ResultsTree"]
    tree.ColumnCount   = 3
    tree.ColumnHeaders = ["#", "Time In / Out", "Caption"]
    tree.ColumnWidth[0] = 50
    tree.ColumnWidth[1] = 195
    tree.ColumnWidth[2] = 390
    tree.Clear()

    found = []   # [{start_frame, framerate}]

    # ── helpers ──────────────────────────────────────────────────────────────

    def get_timeline():
        pm      = resolve.GetProjectManager()
        project = pm.GetCurrentProject() if pm else None
        return project.GetCurrentTimeline() if project else None

    def status(msg):
        items["StatusLabel"].Text = msg

    # ── event handlers ───────────────────────────────────────────────────────

    def OnFind(ev):
        term = items["SearchInput"].Text.strip()
        if not term:
            status("Please enter a search term.")
            return

        pattern = build_pattern(
            term,
            items["MatchCase"].Checked,
            items["WholeWord"].Checked,
            items["UseRegex"].Checked,
        )
        if not pattern:
            status("Invalid regular expression.")
            return

        timeline = get_timeline()
        if not timeline:
            status("No active timeline found. Open a timeline first.")
            return

        try:
            fps = float(timeline.GetSetting("timelineFrameRate"))
        except Exception:
            fps = 24.0

        track = items["TrackNum"].Value
        clips = timeline.GetItemListInTrack("subtitle", track)
        if not clips:
            tree.Clear()
            found.clear()
            status(f"No subtitles found on Subtitle Track {track}.")
            return

        tree.Clear()
        found.clear()

        for clip in clips:
            text = clip.GetName()
            if not pattern.search(text):
                continue
            sf  = clip.GetStart()
            ef  = sf + clip.GetDuration()
            found.append({"start_frame": sf, "framerate": fps})

            row = tree.NewItem()
            row["Text"][0] = str(len(found))
            row["Text"][1] = f"▶ {frame_to_timecode(sf, fps)}\n◀ {frame_to_timecode(ef, fps)}"
            row["Text"][2] = text
            tree.AddTopLevelItem(row)

        n = len(found)
        status(f"Found {n} subtitle{'s' if n != 1 else ''} matching '{term}'." if n else f"No matches for '{term}'.")

    def OnRowClick(ev):
        item = ev.get("item")
        if not item:
            return
        try:
            idx = int(item["Text"][0]) - 1
            if 0 <= idx < len(found):
                d  = found[idx]
                tc = frame_to_timecode(d["start_frame"], d["framerate"])
                tl = get_timeline()
                if tl:
                    tl.SetCurrentTimecode(tc)
                    status(f"Playhead → {tc}")
        except Exception as e:
            status(f"Navigation error: {e}")

    def OnClose(ev):
        dispatcher.ExitLoop()

    win.On.FindBtn.Clicked               = OnFind
    win.On.CancelBtn.Clicked             = OnClose
    win.On.SubtitleSearchWin.Close       = OnClose
    win.On.ResultsTree.ItemClicked       = OnRowClick
    win.On.ResultsTree.ItemDoubleClicked = OnRowClick
    win.On.SearchInput.ReturnPressed     = OnFind

    win.Show()
    dispatcher.RunLoop()
    win.Hide()


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    # When launched from Workspace > Scripts, Resolve pre-populates globals.
    # Support both the injected 'resolve' variable and the 'app' fallback used
    # by the free version.
    _resolve = globals().get("resolve")
    _bmd     = globals().get("bmd")

    if _resolve is None:
        # Free-version fallback: 'app' is the Fusion application object
        _app = globals().get("app")
        if _app:
            _resolve = _app.GetResolve()

    if _resolve is None:
        # External / terminal launch
        _bmd_mod = _load_dvr_script()
        if _bmd_mod is None:
            print("ERROR: DaVinciResolveScript not found. Run this script from inside Resolve.")
            return
        _resolve = _bmd_mod.scriptapp("Resolve")
        _bmd     = _bmd_mod

    if _resolve is None:
        print("ERROR: Could not connect to DaVinci Resolve. Make sure Resolve is running.")
        print("       Free version: go to  DaVinci Resolve > Preferences > System > General")
        print("       and set  'External scripting using'  to  'Local'.")
        return

    if _bmd is None:
        # bmd is always available when run from the Scripts menu;
        # for external runs we use the dvr_script module as a drop-in.
        _bmd = _load_dvr_script()

    show_ui(_resolve, _bmd)


main()
