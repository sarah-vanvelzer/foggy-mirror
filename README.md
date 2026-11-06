# Foggy Mirror

A webcam mirror that fogs up like a bathroom mirror after a hot shower.
Wipe it clear with your hand, write your name in the steam, and breathe
on it to fog it back up.

Built with Python, OpenCV, MediaPipe and sounddevice.

## How to use it

- **Open hand**: wipe the fog away with your whole palm
- **Point with one finger**:write or draw in the fog
- **Breathe on your laptop**: the fog comes back
- **Q**: quit

## How it works

- Each camera frame is blurred and mixed with white to look like frosted glass.
- A hidden black-and-white **mask** remembers where you've wiped.
  Where the mask is white, you see the clear camera; where it's black, you see fog.
- **MediaPipe** tracks your hand. If your middle, ring and pinky fingers
  are up, it wipes with your whole palm; otherwise it draws with your index fingertip.
- The **microphone** listens for breath. When it's loud enough, the mask
  fades back toward black and the fog returns.

## Setup

Requires **Python 3.12**.

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run it

```bash
python foggy-mirror.py
```

## Mac permissions

In System Settings → Privacy & Security, give the app you're running it from
(e.g. VS Code or Terminal) access to:

- **Camera**: so it can see you
- **Microphone**: so it can hear you breathe

Restart that app after turning these on.

## Tuning

In `foggy-mirror.py`:

- `wipe_size`: how thick your finger strokes are
- `breath_threshold`: how loud a breath needs to be to fog the mirror
  (depends on your mic, so test what works for you)
- The blur size `(55, 55)` and the `0.6` / `0.4` mix: how thick the fog looks