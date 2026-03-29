import json

FIELDS = [
    "product_line",
    "origin_port_code",
    "destination_port_code",
    "incoterm",
    "cargo_cbm",
    "cargo_weight_kg",
    "is_dangerous"
]

def normalize_str(val):
    if val is None:
        return None
    return str(val).strip().lower()

def normalize_float(val):
    if val is None:
        return None
    try:
        return round(float(val), 2)
    except:
        return None

def compare_values(key, pred, truth):
    p = pred.get(key)
    t = truth.get(key)

    # null comparison
    if p is None and t is None:
        return True
    if p is None or t is None:
        return False

    # float fields
    if key in ["cargo_cbm", "cargo_weight_kg"]:
        return normalize_float(p) == normalize_float(t)

    # boolean fields
    if key == "is_dangerous":
        return bool(p) == bool(t)

    # string fields
    return normalize_str(p) == normalize_str(t)

def evaluate(predictions, ground_truth):
    gt_map = {item["id"]: item for item in ground_truth}

    field_correct = {f: 0 for f in FIELDS}
    field_total = {f: 0 for f in FIELDS}

    total_correct = 0
    total_fields = 0

    for pred in predictions:
        email_id = pred["id"]
        if email_id not in gt_map:
            continue
        truth = gt_map[email_id]
        for field in FIELDS:
            field_total[field] += 1
            total_fields += 1
            if compare_values(field, pred, truth):
                field_correct[field] += 1
                total_correct += 1
            else:
                print(email_id)

    # compute accuracy
    field_accuracy = {
        f: (field_correct[f] / field_total[f]) * 100 if field_total[f] else 0
        for f in FIELDS
    }

    overall_accuracy = (total_correct / total_fields) * 100 if total_fields else 0
    return field_accuracy, overall_accuracy


def main():
    with open("output1.json", "r") as f:
        predictions = json.load(f)

    with open("ground_truth.json", "r") as f:
        ground_truth = json.load(f)

    field_acc, overall_acc = evaluate(predictions, ground_truth)

    print("\n📊 FIELD-WISE ACCURACY")
    for k, v in field_acc.items():
        print(f"{k}: {v:.2f}%")

    print("\n🎯 OVERALL ACCURACY")
    print(f"{overall_acc:.2f}%")


if __name__ == "__main__":
    main()