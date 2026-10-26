"""Tạo hình minh họa cho các ghi chú OpenCV (img/opencv-notes/<slug>-N.png).

Mỗi hình được sinh ra từ chính các hàm OpenCV mà ghi chú mô tả, dùng ảnh có sẵn trong img/
hoặc ảnh tổng hợp bằng NumPy. Cần OpenCV 4.x (opencv-contrib-python) để có CascadeClassifier
và module ml (OpenCV 5 đã chuyển chúng sang opencv_contrib).

    python3 tools/make_opencv_note_figures.py            # tạo tất cả
    python3 tools/make_opencv_note_figures.py 18 21      # chỉ tạo hình của ghi chú 18 và 21
"""
import sys
from pathlib import Path

import cv2 as cv
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "img"
OUT = IMG / "opencv-notes"
RNG = np.random.default_rng(0)


def read(name, flag=cv.IMREAD_COLOR):
    img = cv.imread(str(IMG / name), flag)
    assert img is not None, name
    return img


def rgb(img):
    return cv.cvtColor(img, cv.COLOR_BGR2RGB) if img.ndim == 3 else img


def show(panels, name, cols=None, size=3.2):
    """panels: list of (ảnh hoặc hàm vẽ, tiêu đề)."""
    cols = cols or len(panels)
    rows = (len(panels) + cols - 1) // cols
    # chiều cao theo tỉ lệ khung của ảnh (biểu đồ coi như 0.75) + chỗ cho tiêu đề
    aspect = np.mean([c.shape[0] / c.shape[1] if not callable(c) else 0.75 for c, _ in panels])
    fig, axes = plt.subplots(rows, cols, figsize=(size * cols, rows * (size * aspect + 0.45)), squeeze=False)
    for ax in axes.ravel():
        ax.axis("off")
    for ax, (content, title) in zip(axes.ravel(), panels):
        if callable(content):
            ax.axis("on")
            content(ax)
        elif content.ndim == 2:
            ax.imshow(content, cmap="gray")
        else:
            ax.imshow(rgb(content))
        ax.set_title(title, fontsize=10)
    fig.tight_layout()
    save(fig, name)


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=80)
    plt.close(fig)
    print("  ", name)


# ---------------------------------------------------------------- 18 Histogram

def fig_18():
    img = read("house.png", cv.IMREAD_GRAYSCALE)
    low = cv.convertScaleAbs(img, alpha=0.35, beta=110)          # ảnh tương phản thấp
    equ = cv.equalizeHist(low)
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(low)

    def hist(im, color):
        return lambda ax: (ax.plot(cv.calcHist([im], [0], None, [256], [0, 256]), color=color),
                           ax.set_xlim([0, 256]), ax.set_yticks([]))

    show([(low, "Ảnh tương phản thấp"), (equ, "equalizeHist"), (clahe, "CLAHE (clip=2, 8x8)"),
          (hist(low, "k"), "Histogram gốc"), (hist(equ, "k"), "Sau equalizeHist"), (hist(clahe, "k"), "Sau CLAHE")],
         "18-histogram-1.png", cols=3)

    color = read("rose.jpg")

    def bgr_hist(ax):
        for i, c in enumerate("bgr"):
            ax.plot(cv.calcHist([color], [i], None, [256], [0, 256]), color=c)
        ax.set_xlim([0, 256])
        ax.set_yticks([])

    hsv = cv.cvtColor(color, cv.COLOR_BGR2HSV)
    h2d = cv.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])

    def hs(ax):
        ax.imshow(np.log1p(h2d), aspect="auto", cmap="magma")
        ax.set_xlabel("S")
        ax.set_ylabel("H")

    show([(color, "Ảnh màu"), (bgr_hist, "Histogram từng kênh B, G, R"), (hs, "Histogram 2D (H, S), thang log")],
         "18-histogram-2.png")

    # backprojection: mẫu là một vùng cánh hoa hồng
    roi = color[85:110, 95:125]
    roihist = cv.calcHist([cv.cvtColor(roi, cv.COLOR_BGR2HSV)], [0, 1], None, [180, 256], [0, 180, 0, 256])
    cv.normalize(roihist, roihist, 0, 255, cv.NORM_MINMAX)
    dst = cv.calcBackProject([hsv], [0, 1], roihist, [0, 180, 0, 256], 1)
    disc = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
    cv.filter2D(dst, -1, disc, dst)
    _, thresh = cv.threshold(dst, 50, 255, 0)
    res = cv.bitwise_and(color, color, mask=thresh)
    boxed = color.copy()
    cv.rectangle(boxed, (95, 85), (125, 110), (255, 0, 0), 2)
    show([(boxed, "Vùng mẫu (khung xanh)"), (dst, "calcBackProject"), (res, "Sau threshold + bitwise_and")],
         "18-histogram-3.png")


# ---------------------------------------------------------------- 19 Fourier

def fig_19():
    img = read("building.png", cv.IMREAD_GRAYSCALE)
    dft = cv.dft(np.float32(img), flags=cv.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    mag = 20 * np.log(cv.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]) + 1)
    rows, cols = img.shape
    crow, ccol = rows // 2, cols // 2

    lpf = np.zeros((rows, cols, 2), np.float32)
    lpf[crow - 20:crow + 20, ccol - 20:ccol + 20] = 1
    low = cv.idft(np.fft.ifftshift(dft_shift * lpf))
    low = cv.magnitude(low[:, :, 0], low[:, :, 1])

    f = np.fft.fftshift(np.fft.fft2(img))
    f[crow - 20:crow + 21, ccol - 20:ccol + 21] = 0
    high = np.abs(np.fft.ifft2(np.fft.ifftshift(f)))

    show([(img, "Ảnh gốc"), (mag, "Phổ biên độ (đã fftshift)"),
          (low, "Lọc thông thấp (giữ ô 40x40)"), (high, "Lọc thông cao (bỏ ô 40x40)")], "19-fourier-transform-1.png")


# ---------------------------------------------------------------- 20 Template matching

def fig_20():
    img = read("fruit.jpg")
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    template = gray[30:105, 240:312]
    h, w = template.shape
    res = cv.matchTemplate(gray, template, cv.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv.minMaxLoc(res)
    out = img.copy()
    cv.rectangle(out, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 0, 255), 3)
    show([(template, "Template"), (res, "Kết quả TM_CCOEFF_NORMED"), (out, f"Vị trí max (score={max_val:.2f})")],
         "20-template-matching-1.png")


# ---------------------------------------------------------------- 21 Hough

def synthetic_coins():
    img = np.full((240, 320), 60, np.uint8)
    for x, y, r in [(60, 70, 30), (150, 60, 24), (250, 80, 36), (90, 170, 40), (200, 175, 28), (280, 190, 20)]:
        cv.circle(img, (x, y), r, 190, -1)
        cv.circle(img, (x, y), r // 2, 210, 2)
    noise = RNG.normal(0, 12, img.shape)
    return np.clip(img + noise, 0, 255).astype(np.uint8)


def fig_21():
    img = read("clemson00.jpg")
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray, 50, 150, apertureSize=3)

    std = img.copy()
    lines = cv.HoughLines(edges, 1, np.pi / 180, 150)
    for rho, theta in (lines[:, 0] if lines is not None else []):
        a, b = np.cos(theta), np.sin(theta)
        x0, y0 = a * rho, b * rho
        p1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * a))
        p2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * a))
        cv.line(std, p1, p2, (0, 0, 255), 2)

    prob = img.copy()
    linesp = cv.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=80, maxLineGap=5)
    for x1, y1, x2, y2 in (linesp[:, 0] if linesp is not None else []):
        cv.line(prob, (x1, y1), (x2, y2), (0, 255, 0), 2)
    show([(edges, "Canny"), (std, "HoughLines (đường vô hạn)"), (prob, "HoughLinesP (đoạn thẳng)")],
         "21-hough-transform-1.png")

    coins = synthetic_coins()
    blur = cv.medianBlur(coins, 5)
    cimg = cv.cvtColor(coins, cv.COLOR_GRAY2BGR)
    circles = cv.HoughCircles(blur, cv.HOUGH_GRADIENT, 1, 20, param1=100, param2=25, minRadius=15, maxRadius=50)
    for x, y, r in np.uint16(np.around(circles))[0]:
        cv.circle(cimg, (int(x), int(y)), int(r), (0, 255, 0), 2)
        cv.circle(cimg, (int(x), int(y)), 2, (0, 0, 255), 3)
    show([(coins, "Ảnh có nhiễu"), (cimg, f"HoughCircles: {len(circles[0])} đường tròn")], "21-hough-transform-2.png")


# ---------------------------------------------------------------- 22 Watershed

def fig_22():
    img = np.zeros((220, 320, 3), np.uint8)
    for x, y, r in [(70, 115, 48), (158, 100, 46), (245, 125, 48), (285, 45, 28)]:
        cv.circle(img, (x, y), r, (200, 200, 200), -1)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    kernel = np.ones((3, 3), np.uint8)
    opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=2)
    sure_bg = cv.dilate(opening, kernel, iterations=3)
    dist = cv.distanceTransform(opening, cv.DIST_L2, 5)
    _, sure_fg = cv.threshold(dist, 0.5 * dist.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv.subtract(sure_bg, sure_fg)

    n, markers = cv.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    markers = cv.watershed(img, markers)
    out = img.copy()
    out[markers == -1] = [0, 0, 255]
    labels = (markers.astype(np.float32) * 255 / markers.max()).clip(0).astype(np.uint8)
    show([(thresh, "Otsu: các đốm dính nhau"), (dist, "distanceTransform"), (sure_fg, "Sure foreground"),
          (cv.applyColorMap(labels, cv.COLORMAP_JET), "Markers sau watershed"), (out, "Biên (markers == -1)")],
         "22-watershed-1.png", cols=5, size=2.6)


# ---------------------------------------------------------------- 23 GrabCut

def fig_23():
    img = read("sheepdog.jpg")
    mask = np.zeros(img.shape[:2], np.uint8)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    rect = (40, 10, 250, 230)
    cv.grabCut(img, mask, rect, bgd, fgd, 5, cv.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == cv.GC_BGD) | (mask == cv.GC_PR_BGD), 0, 1).astype("uint8")
    boxed = img.copy()
    cv.rectangle(boxed, rect[:2], (rect[0] + rect[2], rect[1] + rect[3]), (255, 0, 0), 2)
    show([(boxed, "Khung chữ nhật đầu vào"), (mask * 85, "mask: 0 BGD, 1 FGD, 2 PR_BGD, 3 PR_FGD"),
          (img * mask2[:, :, None], "Tiền cảnh tách được")], "23-grabcut-1.png")


# ---------------------------------------------------------------- 24 Corners

def chessboard(square=30, cols=8, rows=6, margin=30):
    img = np.full((rows * square + 2 * margin, cols * square + 2 * margin), 255, np.uint8)
    for r in range(rows):
        for c in range(cols):
            if (r + c) % 2 == 0:
                y, x = margin + r * square, margin + c * square
                img[y:y + square, x:x + square] = 0
    return img


def fig_24():
    board = chessboard(square=30, cols=6, rows=5, margin=30)
    h, w = board.shape
    H = cv.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]),
                                   np.float32([[30, 20], [w - 10, 50], [w - 40, h - 10], [10, h - 40]]))
    gray = cv.warpPerspective(board, H, (w, h), borderValue=255)
    img = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)

    harris = img.copy()
    dst = cv.cornerHarris(np.float32(gray), 2, 3, 0.04)
    dst = cv.dilate(dst, None)
    harris[dst > 0.01 * dst.max()] = [0, 0, 255]

    img2 = read("clemson00.jpg")
    gray2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
    shi = img2.copy()
    corners = cv.goodFeaturesToTrack(gray2, 50, 0.01, 10)
    for x, y in np.intp(corners).reshape(-1, 2):
        cv.circle(shi, (int(x), int(y)), 3, (0, 255, 0), -1)

    R = cv.cornerHarris(np.float32(gray), 2, 3, 0.04)
    show([(harris, "cornerHarris (R > 1% max)"), (np.sign(R) * np.log1p(np.abs(R)), "R (thang log): sáng = góc, tối = cạnh"),
          (shi, "goodFeaturesToTrack (50 góc mạnh nhất)")],
         "24-corner-detection-1.png")


# ---------------------------------------------------------------- 25 Keypoints

def fig_25():
    img = read("bronzebull00.jpg")
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    sift = cv.SIFT_create()
    kp = sift.detect(gray, None)
    sift_img = cv.drawKeypoints(img, kp[:300], None, flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    fast = cv.FastFeatureDetector_create(threshold=40)
    kpf = fast.detect(gray, None)
    fast_img = cv.drawKeypoints(img, kpf, None, color=(255, 0, 0))
    orb = cv.ORB_create(nfeatures=500)
    kpo = orb.detect(gray, None)
    orb_img = cv.drawKeypoints(img, kpo, None, color=(0, 255, 0), flags=0)
    show([(sift_img, f"SIFT ({len(kp)} điểm, vẽ 300, rich)"), (fast_img, f"FAST threshold=40 ({len(kpf)} điểm)"),
          (orb_img, f"ORB ({len(kpo)} điểm)")], "25-feature-descriptors-1.png", size=4)


# ---------------------------------------------------------------- 26 Matching

def fig_26():
    img1 = read("bronzebull00.jpg", cv.IMREAD_GRAYSCALE)
    img2 = read("bronzebull02.jpg", cv.IMREAD_GRAYSCALE)

    orb = cv.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
    matches = sorted(bf.match(des1, des2), key=lambda m: m.distance)
    orb_img = cv.drawMatches(img1, kp1, img2, kp2, matches[:30], None, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    sift = cv.SIFT_create()
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)
    flann = cv.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
    good = [m for m, n in flann.knnMatch(des1, des2, k=2) if m.distance < 0.7 * n.distance]
    sift_img = cv.drawMatches(img1, kp1, img2, kp2, good[:60], None, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    show([(orb_img, "ORB + BFMatcher(NORM_HAMMING, crossCheck), 30 cặp tốt nhất"),
          (sift_img, f"SIFT + FLANN + ratio test 0.7 ({len(good)} cặp, vẽ 60)")], "26-feature-matching-1.png", cols=1, size=8)


# ---------------------------------------------------------------- 27 Homography

def fig_27():
    scene = read("clemson01.jpg", cv.IMREAD_GRAYSCALE)
    obj = read("clemson00.jpg", cv.IMREAD_GRAYSCALE)[30:150, 40:180]
    sift = cv.SIFT_create()
    kp1, des1 = sift.detectAndCompute(obj, None)
    kp2, des2 = sift.detectAndCompute(scene, None)
    flann = cv.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
    good = [m for m, n in flann.knnMatch(des1, des2, k=2) if m.distance < 0.7 * n.distance]
    src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    M, mask = cv.findHomography(src, dst, cv.RANSAC, 5.0)
    h, w = obj.shape
    corners = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    box = cv.perspectiveTransform(corners, M)
    scene_c = cv.cvtColor(scene, cv.COLOR_GRAY2BGR)
    cv.polylines(scene_c, [np.int32(box)], True, (0, 0, 255), 3, cv.LINE_AA)
    out = cv.drawMatches(obj, kp1, scene_c, kp2, good, None, matchColor=(0, 255, 0),
                         matchesMask=mask.ravel().tolist(), flags=2)
    show([(out, f"Inlier RANSAC: {int(mask.sum())}/{len(good)} cặp, khung đỏ = perspectiveTransform")],
         "27-homography-1.png", cols=1, size=8)


# ---------------------------------------------------------------- 28 Meanshift / Camshift

def moving_blob_frames(n=40):
    bg = read("house.png")
    frames = []
    for t in range(n):
        f = bg.copy()
        cx, cy = int(40 + 4 * t), int(80 + 35 * np.sin(t / 6))
        axes = (14 + t // 4, 10 + t // 6)
        cv.ellipse(f, (cx, cy), axes, 3 * t, 0, 360, (30, 30, 230), -1)
        frames.append(f)
    return frames


def track(frames, use_camshift, shots=(0, 20, 39)):
    x, y, w, h = 28, 72, 24, 16                      # cửa sổ ban đầu ôm sát vật ở frame đầu
    roi = cv.cvtColor(frames[0][y:y + h, x:x + w], cv.COLOR_BGR2HSV)
    mask = cv.inRange(roi, np.array((0., 150., 50.)), np.array((180., 255., 255.)))
    roi_hist = cv.calcHist([roi], [0], mask, [180], [0, 180])
    cv.normalize(roi_hist, roi_hist, 0, 255, cv.NORM_MINMAX)
    term = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)
    window = (x, y, w, h)
    out = []
    for i, f in enumerate(frames):
        dst = cv.calcBackProject([cv.cvtColor(f, cv.COLOR_BGR2HSV)], [0], roi_hist, [0, 180], 1)
        if use_camshift:
            rot, window = cv.CamShift(dst, window, term)
        else:
            _, window = cv.meanShift(dst, window, term)
        if i in shots:
            img = f.copy()
            if use_camshift:
                cv.polylines(img, [np.intp(cv.boxPoints(rot))], True, (0, 255, 0), 2)
            else:
                x, y, w, h = window
                cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            out.append(img)
    return out


def fig_28():
    frames = moving_blob_frames()
    shots = (0, 20, 39)
    ms, cs = track(frames, False, shots), track(frames, True, shots)
    show([(im, f"meanShift - frame {t}") for im, t in zip(ms, shots)] +
         [(im, f"CamShift - frame {t}") for im, t in zip(cs, shots)], "28-meanshift-camshift-1.png", cols=3)


# ---------------------------------------------------------------- 29 Optical flow

def fig_29():
    f1, f2 = read("army10.png"), read("army11.png")
    g1, g2 = cv.cvtColor(f1, cv.COLOR_BGR2GRAY), cv.cvtColor(f2, cv.COLOR_BGR2GRAY)

    p0 = cv.goodFeaturesToTrack(g1, maxCorners=150, qualityLevel=0.01, minDistance=7, blockSize=7)
    p1, st, err = cv.calcOpticalFlowPyrLK(g1, g2, p0, None, winSize=(15, 15), maxLevel=2,
                                         criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))
    lk = f2.copy()
    for new, old in zip(p1[st == 1], p0[st == 1]):
        a, b = new.ravel()
        c, d = old.ravel()
        # phóng đại vector x4 để dễ nhìn
        cv.arrowedLine(lk, (int(c), int(d)), (int(c + 10 * (a - c)), int(d + 10 * (b - d))), (0, 255, 0), 2, tipLength=0.3)

    flow = cv.calcOpticalFlowFarneback(g1, g2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    mag, ang = cv.cartToPolar(flow[..., 0], flow[..., 1])
    hsv = np.zeros_like(f1)
    hsv[..., 0] = ang * 180 / np.pi / 2
    hsv[..., 1] = 255
    hsv[..., 2] = cv.normalize(mag, None, 0, 255, cv.NORM_MINMAX)
    dense = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
    show([(f1, "Frame t"), (lk, "Lucas-Kanade thưa (vector x10)"), (dense, "Farneback dày: màu = hướng, độ sáng = độ lớn")],
         "29-optical-flow-1.png", size=3.6)


# ---------------------------------------------------------------- 30 Background subtraction

def fig_30():
    bg = read("house.png")
    mog2 = cv.createBackgroundSubtractorMOG2(detectShadows=True)
    knn = cv.createBackgroundSubtractorKNN(detectShadows=True)
    for t in range(60):
        f = bg.astype(np.int16) + RNG.normal(0, 4, bg.shape).astype(np.int16)
        f = np.clip(f, 0, 255).astype(np.uint8)
        if t >= 30:
            x = 20 + 4 * (t - 30)
            f[125:135, x + 6:x + 40] = (f[125:135, x + 6:x + 40] * 0.6).astype(np.uint8)   # bóng: nền tối đi
            cv.rectangle(f, (x, 95), (x + 30, 125), (20, 140, 230), -1)        # vật chuyển động
        m1, m2 = mog2.apply(f), knn.apply(f)
    show([(f, "Frame hiện tại"), (m1, "MOG2 (xám 127 = bóng)"), (m2, "KNN"),
          (mog2.getBackgroundImage(), "Nền ước lượng (MOG2)")], "30-background-subtraction-1.png", size=3)


# ---------------------------------------------------------------- 31-32 Calibration, pose

def distorted_views(board, K, dist, n=12):
    """Chụp mô phỏng bàn cờ phẳng từ nhiều góc nhìn qua camera có méo xuyên tâm."""
    h, w = 480, 640
    rows, cols = board.shape
    obj = np.float32([[0, 0, 0], [cols, 0, 0], [cols, rows, 0], [0, rows, 0]])
    views = []
    for i in range(n):
        rvec = np.float32([RNG.uniform(-0.5, 0.5), RNG.uniform(-0.5, 0.5), RNG.uniform(-0.3, 0.3)])
        tvec = np.float32([RNG.uniform(-180, -120), RNG.uniform(-140, -90), RNG.uniform(550, 700)])
        corners, _ = cv.projectPoints(obj, rvec, tvec, K, None)
        H = cv.getPerspectiveTransform(np.float32([[0, 0], [cols, 0], [cols, rows], [0, rows]]), corners.reshape(4, 2))
        ideal = cv.warpPerspective(board, H, (w, h), borderValue=128)
        # thêm méo: với mỗi pixel ảnh méo, tìm pixel ảnh lý tưởng tương ứng
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        pts = np.stack([xs.ravel(), ys.ravel()], 1).reshape(-1, 1, 2)
        und = cv.undistortPoints(pts, K, dist, P=K).reshape(h, w, 2)
        views.append(cv.remap(ideal, und[..., 0], und[..., 1], cv.INTER_LINEAR, borderValue=128))
    return views


def fig_31_32():
    K = np.float64([[600, 0, 320], [0, 600, 240], [0, 0, 1]])
    dist = np.float64([-0.35, 0.12, 0, 0, 0])
    board = chessboard(square=40, cols=10, rows=7, margin=40)
    views = distorted_views(board, K, dist)

    pattern = (9, 6)            # số góc trong: (cột, hàng)
    objp = np.zeros((pattern[0] * pattern[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:pattern[0], 0:pattern[1]].T.reshape(-1, 2)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objpoints, imgpoints, found_img = [], [], None
    for v in views:
        ret, corners = cv.findChessboardCorners(v, pattern, None)
        if ret:
            corners2 = cv.cornerSubPix(v, corners, (11, 11), (-1, -1), criteria)
            objpoints.append(objp)
            imgpoints.append(corners2)
            if found_img is None:
                found_img = cv.drawChessboardCorners(cv.cvtColor(v, cv.COLOR_GRAY2BGR), pattern, corners2, ret)
    ret, mtx, dist_est, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, views[0].shape[::-1], None, None)
    print(f"   calib: {len(objpoints)} ảnh, RMS={ret:.3f}, fx={mtx[0, 0]:.1f}, k1={dist_est[0, 0]:.3f}")

    h, w = views[0].shape
    newK, roi = cv.getOptimalNewCameraMatrix(mtx, dist_est, (w, h), 1, (w, h))
    und = cv.undistort(views[0], mtx, dist_est, None, newK)
    show([(found_img, "findChessboardCorners + drawChessboardCorners"), (views[0], "Ảnh bị méo xuyên tâm"),
          (und, "Sau undistort (alpha=1)")], "31-camera-calibration-1.png", size=3.6)

    # Pose: vẽ trục và hình hộp lên một view
    img = cv.cvtColor(views[1], cv.COLOR_GRAY2BGR)
    _, rvec, tvec = cv.solvePnP(objp, imgpoints[1], mtx, dist_est)
    axes_img = cv.drawFrameAxes(img.copy(), mtx, dist_est, rvec, tvec, 3, 3)
    cube = np.float32([[0, 0, 0], [0, 3, 0], [3, 3, 0], [3, 0, 0], [0, 0, -3], [0, 3, -3], [3, 3, -3], [3, 0, -3]])
    pts, _ = cv.projectPoints(cube, rvec, tvec, mtx, dist_est)
    pts = np.int32(pts).reshape(-1, 2)
    cube_img = img.copy()
    cv.drawContours(cube_img, [pts[:4]], -1, (0, 255, 0), -3)
    for i, j in zip(range(4), range(4, 8)):
        cv.line(cube_img, tuple(pts[i]), tuple(pts[j]), (255, 0, 0), 3)
    cv.drawContours(cube_img, [pts[4:]], -1, (0, 0, 255), 3)
    show([(axes_img, "solvePnP + drawFrameAxes"), (cube_img, "projectPoints: hình hộp 3x3x3 ô")],
         "32-pose-estimation-1.png", size=4)


# ---------------------------------------------------------------- 33 Epipolar

def fig_33():
    img1 = read("clemson00.jpg", cv.IMREAD_GRAYSCALE)
    img2 = read("clemson01.jpg", cv.IMREAD_GRAYSCALE)
    sift = cv.SIFT_create()
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)
    flann = cv.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
    pts1, pts2 = [], []
    for m, n in flann.knnMatch(des1, des2, k=2):
        if m.distance < 0.8 * n.distance:
            pts1.append(kp1[m.queryIdx].pt)
            pts2.append(kp2[m.trainIdx].pt)
    pts1, pts2 = np.int32(pts1), np.int32(pts2)
    F, mask = cv.findFundamentalMat(pts1, pts2, cv.FM_LMEDS)
    pts1, pts2 = pts1[mask.ravel() == 1], pts2[mask.ravel() == 1]
    sel = RNG.choice(len(pts1), size=min(12, len(pts1)), replace=False)
    pts1, pts2 = pts1[sel], pts2[sel]

    def drawlines(img1, img2, lines, pts1, pts2):
        r, c = img1.shape
        img1, img2 = cv.cvtColor(img1, cv.COLOR_GRAY2BGR), cv.cvtColor(img2, cv.COLOR_GRAY2BGR)
        for line, p1, p2 in zip(lines, pts1, pts2):
            color = tuple(int(v) for v in RNG.integers(0, 255, 3))
            x0, y0 = 0, int(-line[2] / line[1])
            x1, y1 = c, int(-(line[2] + line[0] * c) / line[1])
            cv.line(img1, (x0, y0), (x1, y1), color, 1)
            cv.circle(img1, tuple(int(v) for v in p1), 5, color, -1)
            cv.circle(img2, tuple(int(v) for v in p2), 5, color, -1)
        return img1, img2

    lines1 = cv.computeCorrespondEpilines(pts2.reshape(-1, 1, 2), 2, F).reshape(-1, 3)
    img5, _ = drawlines(img1, img2, lines1, pts1, pts2)
    lines2 = cv.computeCorrespondEpilines(pts1.reshape(-1, 1, 2), 1, F).reshape(-1, 3)
    img3, _ = drawlines(img2, img1, lines2, pts2, pts1)
    show([(img5, "Ảnh trái: epiline của các điểm ảnh phải"), (img3, "Ảnh phải: epiline của các điểm ảnh trái")],
         "33-epipolar-geometry-1.png", size=4)


# ---------------------------------------------------------------- 34 Stereo

def fig_34():
    left = read("tsukuba_left.png", cv.IMREAD_GRAYSCALE)
    right = read("tsukuba_right.png", cv.IMREAD_GRAYSCALE)
    bm = cv.StereoBM_create(numDisparities=32, blockSize=9).compute(left, right)
    sgbm = cv.StereoSGBM_create(minDisparity=0, numDisparities=32, blockSize=5, P1=8 * 5 ** 2, P2=32 * 5 ** 2,
                                uniquenessRatio=10, speckleWindowSize=100, speckleRange=2).compute(left, right)
    def disp(d):
        d = d.astype(np.float32) / 16                       # disparity thật = giá trị trả về / 16
        vis = cv.applyColorMap(np.uint8(np.clip(d, 0, 32) * 255 / 32), cv.COLORMAP_JET)
        vis[d < 0] = 0                                      # pixel không khớp được: đen
        return vis
    show([(left, "Ảnh trái"), (disp(bm), "StereoBM (xa: xanh, gần: đỏ)"),
          (disp(sgbm), "StereoSGBM (xa: xanh, gần: đỏ)")], "34-stereo-depth-map-1.png")


# ---------------------------------------------------------------- 35 K-means

def fig_35():
    img = read("army10.png")
    Z = np.float32(img.reshape((-1, 3)))
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    panels = [(img, "Ảnh gốc")]
    for K in (2, 4, 8):
        _, label, center = cv.kmeans(Z, K, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS)
        res = np.uint8(center)[label.flatten()].reshape(img.shape)
        panels.append((res, f"K = {K}"))
    show(panels, "35-kmeans-1.png", size=3)


# ---------------------------------------------------------------- 36 kNN, SVM

def fig_36():
    if not hasattr(cv, "ml"):
        print("   bỏ qua 36: OpenCV này không có module ml")
        return
    a = RNG.normal([30, 30], 12, (60, 2))
    b = RNG.normal([65, 60], 12, (60, 2))
    train = np.float32(np.vstack([a, b]))
    labels = np.int32([0] * 60 + [1] * 60).reshape(-1, 1)
    xx, yy = np.meshgrid(np.arange(0, 100, 0.5), np.arange(0, 100, 0.5))
    grid = np.float32(np.c_[xx.ravel(), yy.ravel()])

    knn = cv.ml.KNearest_create()
    knn.train(train, cv.ml.ROW_SAMPLE, labels)
    _, knn_pred, _, _ = knn.findNearest(grid, 5)

    svm = cv.ml.SVM_create()
    svm.setType(cv.ml.SVM_C_SVC)
    svm.setKernel(cv.ml.SVM_RBF)
    svm.setC(10.0)
    svm.setGamma(0.001)
    svm.train(train, cv.ml.ROW_SAMPLE, labels)
    svm_pred = svm.predict(grid)[1]
    sv = svm.getSupportVectors()

    def plot(pred, extra=None):
        def draw(ax):
            ax.contourf(xx, yy, pred.reshape(xx.shape), alpha=0.25, cmap="coolwarm")
            ax.scatter(a[:, 0], a[:, 1], c="tab:blue", s=12)
            ax.scatter(b[:, 0], b[:, 1], c="tab:red", s=12, marker="^")
            if extra is not None:
                ax.scatter(extra[:, 0], extra[:, 1], s=60, facecolors="none", edgecolors="k")
            ax.set_xticks([])
            ax.set_yticks([])
        return draw

    show([(plot(knn_pred), "kNN (k = 5)"), (plot(svm_pred, sv), "SVM RBF (vòng đen = support vector)")],
         "36-knn-svm-1.png", size=3.6)


# ---------------------------------------------------------------- 37 Denoising

def fig_37():
    img = read("lhasa_apso.jpg")
    noisy = np.clip(img + RNG.normal(0, 25, img.shape), 0, 255).astype(np.uint8)
    gauss = cv.GaussianBlur(noisy, (5, 5), 0)
    nlm = cv.fastNlMeansDenoisingColored(noisy, None, 10, 10, 7, 21)
    show([(noisy, "Nhiễu Gauss σ = 25"), (gauss, "GaussianBlur 5x5"), (nlm, "fastNlMeansDenoisingColored")],
         "37-image-denoising-1.png")


# ---------------------------------------------------------------- 38 Inpainting

def fig_38():
    img = read("rose.jpg")
    mask = np.zeros(img.shape[:2], np.uint8)
    cv.putText(mask, "OpenCV", (20, 120), cv.FONT_HERSHEY_SIMPLEX, 2.2, 255, 7)
    cv.line(mask, (30, 30), (280, 190), 255, 5)
    damaged = img.copy()
    damaged[mask > 0] = 255
    telea = cv.inpaint(damaged, mask, 3, cv.INPAINT_TELEA)
    ns = cv.inpaint(damaged, mask, 3, cv.INPAINT_NS)
    show([(damaged, "Ảnh hỏng"), (mask, "mask (trắng = cần vá)"), (telea, "INPAINT_TELEA"), (ns, "INPAINT_NS")],
         "38-inpainting-1.png", size=3)


# ---------------------------------------------------------------- 39 HDR

def fig_39():
    img = read("bicycle_train.jpg")
    img = cv.resize(img, (500, 333), interpolation=cv.INTER_AREA)
    radiance = (img.astype(np.float32) / 255) ** 2.2 * 4              # giả lập độ rọi tuyến tính, dải rộng
    times = np.float32([1 / 16, 1 / 4, 1, 4])
    exposures = [np.uint8(np.clip((radiance * t) ** (1 / 2.2), 0, 1) * 255) for t in times]
    fusion = cv.createMergeMertens().process(exposures)
    fusion8 = np.clip(fusion * 255, 0, 255).astype(np.uint8)
    show([(e, f"Phơi sáng x{t:g}") for e, t in zip(exposures, times)] + [(fusion8, "Mertens fusion")],
         "39-hdr-1.png", cols=5, size=2.6)


# ---------------------------------------------------------------- 40 Haar cascade

def fig_40():
    if not hasattr(cv, "CascadeClassifier"):
        print("   bỏ qua 40: OpenCV này không có CascadeClassifier")
        return
    img = read("apollo11_crew.jpg")
    gray = cv.equalizeHist(cv.cvtColor(img, cv.COLOR_BGR2GRAY))
    face = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_frontalface_default.xml")
    eyes = cv.CascadeClassifier(cv.data.haarcascades + "haarcascade_eye.xml")
    out = img.copy()
    loose = face.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    faces = face.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(60, 60))
    for x, y, w, h in loose:
        cv.rectangle(out, (x, y), (x + w, y + h), (0, 0, 255), 2)       # minNeighbors=5: đỏ
    for x, y, w, h in faces:
        cv.rectangle(out, (x, y), (x + w, y + h), (255, 0, 0), 3)
        roi = gray[y:y + h // 2 + h // 6, x:x + w]
        for ex, ey, ew, eh in eyes.detectMultiScale(roi, 1.1, 8):
            cv.rectangle(out, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (0, 255, 0), 2)
    show([(out, f"minNeighbors=5: {len(loose)} vùng (đỏ), minNeighbors=10: {len(faces)} mặt (xanh dương), mắt (xanh lá)")], "40-face-detection-1.png", cols=1, size=7)


FIGS = {18: fig_18, 19: fig_19, 20: fig_20, 21: fig_21, 22: fig_22, 23: fig_23, 24: fig_24, 25: fig_25,
        26: fig_26, 27: fig_27, 28: fig_28, 29: fig_29, 30: fig_30, 31: fig_31_32, 33: fig_33, 34: fig_34,
        35: fig_35, 36: fig_36, 37: fig_37, 38: fig_38, 39: fig_39, 40: fig_40}

if __name__ == "__main__":
    print("OpenCV", cv.__version__)
    wanted = [int(a) for a in sys.argv[1:]] or list(FIGS)
    for k in wanted:
        print(k)
        FIGS[k]()
