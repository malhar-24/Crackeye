import json
import cv2
from datetime import datetime

import numpy as np
from ultralytics import YOLO
from datetime import datetime

model = YOLO("app/modules/best.pt")

names = {
    0: "crack",
    1: "spalling",
    2: "manhole",
    3: "corrosion",
    4: "pothole",
    5: "stain"
}

# ---------------------------
# DAMAGE INTELLIGENCE ENGINE
# ---------------------------
def get_level(area):
    if area > 6000:
        return "critical"
    elif area > 3000:
        return "high"
    elif area > 1000:
        return "medium"
    return "low"


def risk_score(area, conf, level):
    base = area * conf / 1000
    mapping = {"low": 2, "medium": 5, "high": 8, "critical": 10}
    return round(min(10, base + mapping[level]), 2)


def recommendation(cls, mask_area_m2,level):

    # per m² repair rates (you can tune later with real data)
    rates = {
        "crack": 12,        # ₹ per m²
        "pothole": 25,
        "spalling": 40,
        "corrosion": 18,
        "manhole": 15
    }

    if cls == "crack":
        material = "epoxy resin"
        return {
            "action": "crack sealing",
            "method": "injection sealing",
            "material": material,
            "cost": round(mask_area_m2 * rates["crack"], 2),
            "time": max(2, int(mask_area_m2 / 500))
        }

    if cls == "pothole":
        if level == "low":
            material = "cold mix asphalt"
        elif level == "medium":
            material = "hot mix asphalt"
        else:
            material = "hot mix asphalt + base reinforcement + tack coat"
        return {
            "action": "patch repair",
            "method": "asphalt patching",
            "material": material,
            "cost": round(mask_area_m2 * rates["pothole"], 2),
            "time": max(3, int(mask_area_m2 / 400))
        }

    if cls == "spalling":
        if level == "low":
            material = "cement mortar patch"
        elif level == "medium":
            material = "polymer-modified repair mortar"
        elif level == "high":
            material = "shotcrete concrete + bonding agent"
        else:  # critical
            material = "shotcrete + steel rebar reinforcement + corrosion inhibitor"
        return {
            "action": "concrete resurfacing",
            "method": "shotcrete application",
            "material": material,
            "cost": round(mask_area_m2 * rates["spalling"], 2),
            "time": max(5, int(mask_area_m2 / 300))
        }

    if cls == "corrosion":
        if level == "low":
            material = "rust remover + protective paint"
        elif level == "medium":
            material = "rust remover + zinc primer + epoxy coating"
        elif level == "high":
            material = "anti-corrosion coating + sealant + surface repair mortar"
        else:  # critical
            material = "corrosion inhibitor + rebar treatment + epoxy + structural repair"
        return {
            "action": "anti-corrosion treatment",
            "method": "chemical coating + sealing",
            "material": material,
            "cost": round(mask_area_m2 * rates["corrosion"], 2),
            "time": max(2, int(mask_area_m2 / 600))
        }

    if cls == "manhole":
        if level == "critical":
            material_primary = "heavy-duty ductile iron"
        else:
            material_primary = "standard ductile iron (B125/C250)"
        return {
            "action": "cover replacement",
            "method": "steel reinforcement replacement",
            "material":material_primary,
            "cost": round(mask_area_m2 * rates["manhole"], 2),
            "time": max(1, int(mask_area_m2 / 800))
        }

    return {
        "action": "inspection",
        "method": "manual survey",
        "material":"NA",
        "cost": 5000,
        "time": 2
    }



def save_results(path, r, masks,
                 overlay_path="overlay.jpg",
                 mask_path="mask.jpg"):

    img = cv2.imread(path)
    h, w = img.shape[:2]

    overlay = img.copy()

    # -------------------------
    # BLACK & WHITE MASK IMAGE
    # -------------------------
    full_mask = np.zeros((h, w), dtype=np.uint8)

    for i in range(len(masks)):
        mask = masks[i]

        # resize to image size
        mask_resized = cv2.resize(mask, (w, h))

        # binary mask
        mask_bin = (mask_resized > 0.5).astype(np.uint8)

        # combine all masks
        full_mask = cv2.bitwise_or(full_mask, mask_bin * 255)

        # -------------------------
        # OVERLAY (RED DAMAGE)
        # -------------------------
        overlay[mask_bin == 1] = (0, 0, 255)

    # -------------------------
    # BLEND IMAGE
    # -------------------------
    final_overlay = cv2.addWeighted(img, 0.7, overlay, 0.3, 0)

    # -------------------------
    # SAVE FILES
    # -------------------------
    cv2.imwrite(overlay_path, final_overlay)
    cv2.imwrite(mask_path, full_mask)

    print("Saved overlay:", overlay_path)
    print("Saved mask:", mask_path)

# ---------------------------
# MAIN FUNCTION
# ---------------------------
def detectdamage(path):
    results = model.predict(source=path)
    r = results[0]

    if r.masks is None:
        return {"status": "no damage detected"}

    masks = r.masks.data.cpu().numpy()
    save_results(path, r, masks, "app/static/processimage/overlay.jpg","app/static/processimage/mask.jpg")
    output_list = []

    for i in range(len(r.boxes)):
        cls_id = int(r.boxes.cls[i])
        cls = names[cls_id]
        conf = float(r.boxes.conf[i])

        x1, y1, x2, y2 = map(int, r.boxes.xyxy[i])

        bbox_area = (x2 - x1) * (y2 - y1)
        mask_area = float(np.sum(masks[i]))*0.1

        level = get_level(mask_area)
        risk = risk_score(mask_area, conf, level)

        rec = recommendation(cls,mask_area*0.005,level)

        output = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),

            "location": {
                "latitude": None,
                "longitude": None,
                "area": "unknown",
                "zone": "unknown"
            },

            "damage": {
                "type": cls,
                "category": "infrastructure",
                "level": level,
                "confidence": round(conf, 2)*100
            },

            "geometry": {
                "mask_area": mask_area,
                "bbox_area": bbox_area
            },

            "risk_assessment": {
                "risk_score": risk,
                "priority": "urgent" if risk > 7 else "medium" if risk > 4 else "low",
                "traffic_impact": "high" if cls in ["pothole", "crack"] else "medium"
            },

            "recommended_action": {
                "action": rec["action"],
                "method": rec["method"],
                "material": rec["material"],
                "estimated_cost": rec["cost"],
                "estimated_time_hours": rec["time"]
            },

            "inspection": {
                "method": "YOLO segmentation",
                "model_used": "best.pt",
                "processed": True
            }
        }

        output_list.append(output)

    return {
        "status": "success",
        "results": output_list
    }

def getdata():
    path = "app/static/uploads/image.jpg"

    detections = detectdamage(path)  # {"status": "...", "results": [...]}

    output_list = detections.get("results", [])

    if not output_list:
        return json.dumps({
            "status": "no damage detected",
            "results": []
        }, indent=4)

    # Optional: enrich with timestamp + location (if needed)
    for item in output_list:
        item["timestamp"] = datetime.now().isoformat()

        item.setdefault("location", {
            "latitude": None,
            "longitude": None,
            "area": "unknown",
            "zone": "unknown"
        })

    # FINAL OUTPUT = LIST WRAPPED IN JSON
    return json.dumps({
        "status": "success",
        "count": len(output_list),
        "results": output_list
    }, indent=4)


