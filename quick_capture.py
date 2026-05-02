"""
quick_capture.py -- one-script recording for the SLICE experiment.

If you build the SLICE apparatus, run this on the connected laptop.
Records from the multi-channel audio interface and saves a numpy
file we can analyse.

Usage:
    pip install sounddevice numpy
    python quick_capture.py --duration 60 --device 4 --channels 6 \\
        --fs 192000 --out my_recording.npy

Then send the .npy file (or run the SLICE pipeline locally):
    python -c "import numpy as np; \\
               from sim_env.experiments.exp12_slice_detector import \\
                   octahedral_mics, run_pipeline; \\
               run_pipeline(np.load('my_recording.npy'), 192000, \\
                            octahedral_mics(0.15), label='live')"
"""

import argparse
import sys


def list_devices():
    import sounddevice as sd
    print(sd.query_devices())


def record(duration, device, channels, fs, outfile):
    import numpy as np
    import sounddevice as sd
    print(f"Recording {duration} s @ {fs} Hz on {channels} channels "
          f"from device {device}...")
    rec = sd.rec(int(duration * fs), samplerate=fs, channels=channels,
                 dtype="float32", device=device)
    sd.wait()
    arr = rec.T                             # shape (channels, samples)
    np.save(outfile, arr)
    print(f"Saved {arr.shape} to {outfile}.  Peak per channel: "
          + ", ".join(f"{p:.4f}" for p in np.max(np.abs(arr), axis=1)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true",
                    help="list audio devices and exit")
    ap.add_argument("--device", type=int, default=None,
                    help="device index (see --list)")
    ap.add_argument("--duration", type=float, default=60.0,
                    help="recording length, seconds")
    ap.add_argument("--channels", type=int, default=6,
                    help="number of channels")
    ap.add_argument("--fs", type=int, default=192_000,
                    help="sampling rate, Hz")
    ap.add_argument("--out", default="recording.npy",
                    help="output .npy file")
    args = ap.parse_args()
    if args.list:
        list_devices()
        sys.exit(0)
    if args.device is None:
        print("Specify --device. Run with --list to see options.")
        sys.exit(1)
    record(args.duration, args.device, args.channels, args.fs, args.out)


if __name__ == "__main__":
    main()
