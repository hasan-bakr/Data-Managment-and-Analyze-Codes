#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
singlecam_calib.py  (with Keystone correction)
Interactive calibration/undistort UI for a *single* video source.

Usage:
  python singlecam_calib.py --video /path/to/input.mp4
  # optional undistorted output:
  python singlecam_calib.py --video /path/to/input.mp4 --output /path/to/undistorted.mp4

Keys:
  ESC   : quit
  S     : save JSON next to input (…_calib.json)
  O     : toggle writing undistorted output MP4
  SPACE : pause/resume

Sliders:
  k1,k2,p1,p2      : radial/tangential distortion
  cx %, cy %       : principal point (as % of width/height)
  zoom %           : fx (relative to width)
  fy/fx %          : fy/fx ratio (100 → fy=fx)
  rot deg          : rotation in degrees
  keystone X %, Y %: perspective correction (50 = 0)
  crop L/R/T/B %   : border crops
"""

import cv2, numpy as np, json, argparse, time
from pathlib import Path

# ------------------------- Helpers -------------------------
def K(fx, fy, cx, cy):
    return np.array([[fx,0,cx],[0,fy,cy],[0,0,1]], np.float32)

def s2v(name, rng, zero=0.0):
    # map trackbar [0..1000] -> value in [zero-rng, zero+rng]
    return (cv2.getTrackbarPos(name, "Calib") - 500) / 500.0 * rng + zero

def create_slider(name, init=500, maxv=1000):
    cv2.createTrackbar(name, "Calib", init, maxv, lambda x: None)

def rot_image(img, angle_deg):
    if angle_deg == 0:
        return img
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), angle_deg, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

def write_json(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[i] Saved params: {path}")

def build_keystone_H(w, h, kx, ky, scale=0.004):
    """
    Simple keystone (perspective) transform.
    Sliders give kx,ky in -50..+50 around zero (50 on the UI). scale controls sensitivity.
    Positive kx pulls left/right edges inward; positive ky pulls top/bottom inward.
    """
    if kx == 0 and ky == 0:
        return None
    dx = kx * scale * w
    dy = ky * scale * h
    src = np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
    dst = np.float32([
        [0+dx,      0+dy],
        [w-1-dx,    0+dy],
        [w-1-dx,    h-1-dy],
        [0+dx,      h-1-dy]
    ])
    return cv2.getPerspectiveTransform(src, dst)

# ------------------------- Main ----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", type=str, required=True, help="Path to input video file")
    ap.add_argument("--output", type=str, default="", help="Optional path to write undistorted video (toggle with 'O')")
    ap.add_argument("--window", type=str, default="View", help="Preview window name")
    args = ap.parse_args()

    vid_path = Path(args.video)
    if not vid_path.exists():
        raise SystemExit(f"Input video not found: {vid_path}")

    cap = cv2.VideoCapture(str(vid_path))
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {vid_path}")

    # Basic properties
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w0  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)  or 1280)
    h0  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 720)

    # Windows
    cv2.namedWindow("Calib", cv2.WINDOW_NORMAL)
    cv2.namedWindow(args.window, cv2.WINDOW_NORMAL)

    # Sliders (center as %; zoom as % of width)
    # Distortion params centered at 0 with symmetric +/- ranges
    create_slider("k1", 500, 1000)   # range ±1.0
    create_slider("k2", 500, 1000)   # range ±0.2
    create_slider("p1", 500, 1000)   # range ±0.02
    create_slider("p2", 500, 1000)   # range ±0.02
    # Center / zoom / fy-fx
    cv2.createTrackbar("cx %", "Calib", 50, 100, lambda x: None)
    cv2.createTrackbar("cy %", "Calib", 50, 100, lambda x: None)
    cv2.createTrackbar("zoom %", "Calib", 100, 500, lambda x: None)     # fx relative to width
    cv2.createTrackbar("fy/fx %", "Calib", 100, 200, lambda x: None)    # 100 = fy=fx
    # Rotation & Keystone & Crops
    cv2.createTrackbar("rot deg", "Calib", 0, 359, lambda x: None)
    cv2.createTrackbar("keystone X %", "Calib", 50, 100, lambda x: None)  # 50 -> 0
    cv2.createTrackbar("keystone Y %", "Calib", 50, 100, lambda x: None)
    cv2.createTrackbar("crop L %", "Calib", 0, 40, lambda x: None)
    cv2.createTrackbar("crop R %", "Calib", 0, 40, lambda x: None)
    cv2.createTrackbar("crop T %", "Calib", 0, 40, lambda x: None)
    cv2.createTrackbar("crop B %", "Calib", 0, 40, lambda x: None)
    cv2.createTrackbar("Edge Bow %", "Calib", 50, 100, lambda x: None)  # 50 => 0 etki
    cv2.createTrackbar("Hump %",    "Calib", 50, 100, lambda x: None)  # 50 => 0 etki, 0..100 → -50..+50
    cv2.createTrackbar("Hump Pow",  "Calib", 20,  80, lambda x: None)  # 2.0 .. 8.0 (20/10=2.0)
    cv2.createTrackbar("Banana %",  "Calib", 50, 100, lambda x: None)  # 50 => 0 etki; <50 aşağı, >50 yukarı
    cv2.createTrackbar("Banana Pow","Calib", 20, 100, lambda x: None)  # 2.0 .. 10.0 (20/10=2.0)

    
    # Defaults
    last_vals = None
    map1 = map2 = None

    paused = False
    writing = False
    writer = None
    out_path = Path(args.output) if args.output else vid_path.with_name(f"{vid_path.stem}_undistorted.mp4")
    json_path = vid_path.with_name(f"{vid_path.stem}_calib.json")

    def build_maps(vals):
        k1, k2, p1, p2, cx, cy, fx, fy = vals
        Kmat = K(fx, fy, cx, cy)
        dist = np.array([k1, k2, p1, p2], np.float32)
        return cv2.initUndistortRectifyMap(
            Kmat, dist, None, Kmat, (w0, h0), cv2.CV_16SC2
        )

    def fetch_vals():
        k1 = s2v("k1", 1.0, 0.0)
        k2 = s2v("k2", 0.2, 0.0)
        p1 = s2v("p1", 0.02, 0.0)
        p2 = s2v("p2", 0.02, 0.0)
        cx = w0 * (cv2.getTrackbarPos("cx %", "Calib") / 100.0)
        cy = h0 * (cv2.getTrackbarPos("cy %", "Calib") / 100.0)
        fx = w0 * (cv2.getTrackbarPos("zoom %", "Calib") / 100.0)
        fy = fx * (cv2.getTrackbarPos("fy/fx %", "Calib") / 100.0)
        rot_deg = cv2.getTrackbarPos("rot deg", "Calib")
        # Keystone sliders: map 0..100 -> -50..+50
        kx = cv2.getTrackbarPos("keystone X %", "Calib") - 50
        ky = cv2.getTrackbarPos("keystone Y %", "Calib") - 50
        cL = cv2.getTrackbarPos("crop L %", "Calib")
        cR = cv2.getTrackbarPos("crop R %", "Calib")
        cT = cv2.getTrackbarPos("crop T %", "Calib")
        cB = cv2.getTrackbarPos("crop B %", "Calib")
        bow = cv2.getTrackbarPos("Edge Bow %", "Calib") - 50  # -50..+50

        hump = cv2.getTrackbarPos("Hump %", "Calib") - 50      # -50..+50 (0 nötr)
        hpow = cv2.getTrackbarPos("Hump Pow", "Calib") / 10.0  # 2.0 .. 8.0
        banana = cv2.getTrackbarPos("Banana %",  "Calib") - 50      # -50..+50 (0 nötr)
        bpow   = cv2.getTrackbarPos("Banana Pow","Calib") / 10.0    # 2.0..10.0 (X^p)

        return (k1, k2, p1, p2, cx, cy, fx, fy, rot_deg, kx, ky, cL, cR, cT, cB, hump, hpow, banana, bpow)
        
    _edge_cache = {"size": None, "bow": None, "mapx": None, "mapy": None}
    _hump_cache = {"size": None, "hump": None, "hpow": None, "mapx": None, "mapy": None}
    _banana_cache = {"size": None, "banana": None, "bpow": None, "mapx": None, "mapy": None}

    def build_banana_maps(w, h, banana, bpow, strength=0.10):
        """
        Parabolik (X^p) dikey ofset uygular: y' = y + A * (|x̂|^p)
        x̂ = (x - cx)/cx  in [-1,1], merkezde 0, kenarda 1.
        banana > 0 -> kenarları YUKARI iter; banana < 0 -> kenarları AŞAĞI iter.
        strength: toplam yüksekliğin yüzdesi (0.05..0.20 deneyebilirsin)
        """
        if (_banana_cache["size"] == (w, h)
            and _banana_cache["banana"] == banana
            and _banana_cache["bpow"] == bpow
            and _banana_cache["mapx"] is not None):
            return _banana_cache["mapx"], _banana_cache["mapy"]

        cx = (w - 1) / 2.0
        xs = np.linspace(0, w - 1, w, dtype=np.float32)
        ys = np.linspace(0, h - 1, h, dtype=np.float32)
        X, Y = np.meshgrid(xs, ys)

        xhat = np.abs((X - cx) / max(1.0, cx))     # 0..1
        shape = np.power(xhat, bpow).astype(np.float32)  # X^p

        A = (banana / 50.0) * (strength * h)       # piksel genliği
        Yp = Y + A * shape                          # parabolik ofset (merkez ≈ 0, kenar max)

        mapx = X.astype(np.float32)
        mapy = Yp.astype(np.float32)

        _banana_cache["size"]   = (w, h)
        _banana_cache["banana"] = banana
        _banana_cache["bpow"]   = bpow
        _banana_cache["mapx"]   = mapx
        _banana_cache["mapy"]   = mapy
        return mapx, mapy

    def build_hump_flat_maps(w, h, hump, hpow, strength=0.06):
        """
        X merkezinde maksimum, kenarlarda ~0 olan dikey ofset uygular:
        y' = y - (hump/50)*strength * (1 - |xn|^hpow) * h
        hump > 0: ortadaki 'tümseği' aşağı çeker (genelde istediğimiz)
        hump < 0: tersi
        """
        if (_hump_cache["size"] == (w, h) and
            _hump_cache["hump"] == hump and
            _hump_cache["hpow"] == hpow and
            _hump_cache["mapx"] is not None):
            return _hump_cache["mapx"], _hump_cache["mapy"]

        cx = (w - 1) / 2.0
        xs = np.linspace(0, w - 1, w, dtype=np.float32)
        ys = np.linspace(0, h - 1, h, dtype=np.float32)
        X, Y = np.meshgrid(xs, ys)

        xn = np.abs((X - cx) / max(1.0, cx))  # 0..1
        # Kenarlarda 1 → (1 - 1^p)=0, merkezde 0 → (1 - 0^p)=1
        shape = (1.0 - np.power(xn, hpow)).astype(np.float32)

        a = (hump / 50.0) * strength * h  # piksel cinsinden amplitude
        Yp = Y - a * shape

        mapx = X.astype(np.float32)
        mapy = Yp.astype(np.float32)

        _hump_cache["size"] = (w, h)
        _hump_cache["hump"] = hump
        _hump_cache["hpow"] = hpow
        _hump_cache["mapx"] = mapx
        _hump_cache["mapy"] = mapy
        return mapx, mapy

    def build_edge_bow_maps(w, h, bow, strength=0.015):
        """
        Kenarları yatayda içeri/dışarı doğru eğrisel eşleyen harita.
        bow: -50..+50 (0 nötr). strength: hassasiyet katsayısı.
        """
        if (_edge_cache["size"] == (w, h)) and (_edge_cache["bow"] == bow) and \
        (_edge_cache["mapx"] is not None):
            return _edge_cache["mapx"], _edge_cache["mapy"]

        # normalize: [-1,1] aralığı (merkez 0)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        xs = np.linspace(0, w - 1, w, dtype=np.float32)
        ys = np.linspace(0, h - 1, h, dtype=np.float32)
        X, Y = np.meshgrid(xs, ys)

        xn = (X - cx) / max(1.0, cx)  # [-1,1]
        # Yatay radyal eğri: x' = x * (1 + s * x^2)
        s = (bow / 50.0) * strength   # –strength .. +strength
        xprime = xn * (1.0 + s * (xn ** 2))

        Xn = xprime
        # geri piksel koordinatına
        mapx = (Xn * cx + cx).astype(np.float32)
        mapy = Y.astype(np.float32)

        _edge_cache["size"] = (w, h)
        _edge_cache["bow"] = bow
        _edge_cache["mapx"] = mapx
        _edge_cache["mapy"] = mapy
        return mapx, mapy

    def ensure_writer(frame_shape):
        nonlocal writer, writing
        h, w = frame_shape[:2]
        if writer is None:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))
            if not writer.isOpened():
                print("[!] Could not open writer, disabling output.")
                writer = None
                writing = False
            else:
                print(f"[i] Writing to: {out_path} @ {fps:.2f} fps")

    print("[i] Controls: ESC=quit | S=save JSON | O=toggle write | SPACE=pause/resume")
    while True:
        if not paused:
            ok, frame = cap.read()
            if not ok:
                # loop for convenience
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ok, frame = cap.read()
                if not ok:
                    print("[!] No more frames and cannot loop. Exiting.")
                    break

        vals = fetch_vals()
        # Rebuild maps if intrinsic/distortion changed
        core_vals = vals[:8]  # k1,k2,p1,p2,cx,cy,fx,fy
        if last_vals is None or core_vals != last_vals[:8]:
            map1, map2 = build_maps(core_vals)
            last_vals = vals

        # Undistort
        und = cv2.remap(frame, map1, map2, cv2.INTER_LINEAR)

        # Rotation
        if vals[8] != 0:
            und = rot_image(und, vals[8])

        # Keystone (perspective) — after undistort+rotate
        kx, ky = vals[9], vals[10]
        H = build_keystone_H(und.shape[1], und.shape[0], kx, ky, scale=0.004)
        if H is not None:
            und = cv2.warpPerspective(und, H, (und.shape[1], und.shape[0]),
                                      flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            
        # Banana warp — X^p ile Y'yi bük (parabolik düzeltme)
        banana, bpow = vals[-2], vals[-1]   # fetch_vals'ta en sona ekledik
        bmapx, bmapy = build_banana_maps(und.shape[1], und.shape[0], banana, bpow, strength=0.10)
        und = cv2.remap(und, bmapx, bmapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


        # Cropping
        cL, cR, cT, cB = vals[11], vals[12], vals[13], vals[14]
        xL = int(und.shape[1] * (cL / 100.0))
        xR = und.shape[1] - int(und.shape[1] * (cR / 100.0))
        yT = int(und.shape[0] * (cT / 100.0))
        yB = int(und.shape[0] * (cB / 100.0))
        if xR > xL and yB > yT:
            und_crop = und[yT:yB, xL:xR]
        else:
            und_crop = und

        # Show
        cv2.imshow(args.window, und_crop)
        cv2.imshow("Calib", np.zeros((1,1,3), np.uint8))  # keep panel responsive

        if writing:
            ensure_writer(und_crop.shape)
            if writer is not None:
                writer.write(und_crop)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key in (ord('s'), ord('S')):
            # vals: [0..19] -> (k1,k2,p1,p2, cx,cy,fx,fy, rot, kx,ky, cL,cR,cT,cB, hump,hpow, banana,bpow)
            k1, k2, p1, p2 = vals[0], vals[1], vals[2], vals[3]
            cx, cy, fx, fy = vals[4], vals[5], vals[6], vals[7]
            rot_deg        = vals[8]
            kx, ky         = vals[9], vals[10]
            cL, cR, cT, cB = vals[11], vals[12], vals[13], vals[14]
            hump, hpow     = vals[15], vals[16]
            banana, bpow   = vals[17], vals[18]

            data = {
                "video": str(vid_path),
                "w0": w0, "h0": h0, "fps": fps,
                "k": [k1, k2, p1, p2],
                "cx": cx, "cy": cy,
                "fx": fx, "fy": fy,
                "rotation_deg": rot_deg,
                "keystone": {"kx": int(kx), "ky": int(ky), "scale": 0.004},
                "banana": {"amount": int(banana), "power": float(bpow), "strength": 0.10},
                "crop_percent": {"L": cL, "R": cR, "T": cT, "B": cB},
            }
            write_json(vid_path.with_name(f"{vid_path.stem}_calib.json"), data)

        elif key in (ord('o'), ord('O')):
            writing = not writing
            print(f"[i] Writing: {'ON' if writing else 'OFF'} -> {out_path}")
            if not writing and writer is not None:
                writer.release(); writer = None
        elif key == 32:  # SPACE
            paused = not paused

    if writer is not None:
        writer.release()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
