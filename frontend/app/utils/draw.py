import cv2
import numpy as np


def draw_boxes(frame, detections, density_level):
    # Mono overlay ramp (BGR): light / mid / full ink by density level.
    color = (175, 175, 175)
    if density_level == "MEDIUM":
        color = (85, 85, 85)
    elif density_level == "HIGH":
        color = (22, 22, 22)
        
    for d in detections:
        bbox = d.get("bbox", [0,0,0,0])
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    return frame

def draw_heatmap(frame, detections):
    mask = np.zeros(frame.shape[:2], dtype=np.float32)
    for d in detections:
        bbox = d.get("bbox", [0,0,0,0])
        x1, y1, x2, y2 = map(int, bbox)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        w, h = x2 - x1, y2 - y1
        radius = int(max(w, h) * 0.5)
        if radius > 0:
            y, x = np.ogrid[-cy:frame.shape[0]-cy, -cx:frame.shape[1]-cx]
            mask_area = np.exp(-(x*x + y*y) / (2 * (radius/2)**2))
            mask += mask_area
            
    mask = np.clip(mask, 0, 1)
    mask = (mask * 255).astype(np.uint8)
    # Mono heatmap: white -> gray -> ink (no hue).
    heatmap = cv2.applyColorMap(mask, cv2.COLORMAP_BONE)
    return cv2.addWeighted(frame, 0.5, heatmap, 0.5, 0)
