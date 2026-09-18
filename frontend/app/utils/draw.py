import cv2
import numpy as np

def draw_boxes(frame, detections, density_level):
    color = (0, 255, 0)
    if density_level == "MEDIUM":
        color = (0, 165, 255)
    elif density_level == "HIGH":
        color = (0, 0, 255)
        
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
    heatmap = cv2.applyColorMap(mask, cv2.COLORMAP_JET)
    return cv2.addWeighted(frame, 0.5, heatmap, 0.5, 0)
