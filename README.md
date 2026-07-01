# MusicToNotesConverter

Windows desktop app: drag-drop audio → sheet music, piano roll, virtual instrument.

## Features

- **Drag & drop** or open MP3/WAV/FLAC/OGG/M4A/AAC
- **Auto-process** on import (toggle in Settings)
- **Instruments**: Piano, Guitar, Violin (pitch range + MIDI program per voice)
- **Views**: Sheet music staff, piano roll, transcript
- **Virtual keyboard** — click or QWERTY (Z-M / Q-P rows)
- **Playback sync** — keys highlight with playhead
- Whisper transcription + librosa pYIN pitch → MIDI
- Export SRT, VTT, MIDI, rendered WAV
- Settings, cache, models, temp → `%APPDATA%\MusicToNotes`

## Setup

```powershell
cd MusicToNotesConverter
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev,playback]"
```

First run downloads Whisper models (~hundreds of MB).

For WAV export / rich keyboard sounds, set a SoundFont (`.sf2`) in Settings.

## Run

```powershell
python -m mtnc
```

## Build executable

```powershell
pip install pyinstaller
python scripts/build.py
```

Output: `dist/MusicToNotes.exe` (single file — copy only the `.exe` to Desktop or anywhere)

Runtime data (settings, Whisper models, temp audio) stored in `%APPDATA%\MusicToNotes`.

## Keyboard

| Key | Action |
|-----|--------|
| Ctrl+O | Open audio |
| Ctrl+R | Process |
| Space | Play / pause |
| Z-M, Q-P | Piano keys (octave in Settings) |

## Stack

PySide6, pyqtgraph, librosa, faster-whisper, pretty-midi

## Requirements

- Windows 10/11, Python 3.11+
- 8 GB RAM (16 GB recommended)
  
## Screenshot

<img width="1690" height="1157" alt="image" src="https://github.com/user-attachments/assets/3bd409d7-579b-4c24-9b37-7e0215058015" />
