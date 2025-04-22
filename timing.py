import json
import time
import csv
from MRTD import encode_mrz, decode_mrz

def time_encode(fields_list, k):
    start = time.perf_counter()
    for fields in fields_list[:k]:
        encode_mrz(fields)
    return time.perf_counter() - start

def time_decode(encoded_lines, k):
    start = time.perf_counter()
    for line1, line2 in encoded_lines[:k]:
        decode_mrz(line1, line2)
    return time.perf_counter() - start

def main():
    # 1) load your decoded→fields JSON
    with open("records_decoded.json", "r") as f:
        data = json.load(f)
    records = data["records_decoded"]

    # 2) build the dicts you pass to encode_mrz
    fields_list = []
    for rec in records:
        name_parts = rec["line1"].get("given_name", "").split()
        first = name_parts[0] if name_parts else ""
        middle = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        fields_list.append({
            "document_type": "P",
            "issuing_country": rec["line1"].get("issuing_country", "")[:3],
            "last_name": rec["line1"].get("last_name", ""),
            "first_name": first,
            "middle_name": middle,
            "passport_number": rec["line2"].get("passport_number", ""),
            "country_code": rec["line2"].get("country_code", ""),
            "birth_date": rec["line2"].get("birth_date", ""),
            "sex": rec["line2"].get("sex", ""),
            "expiration_date": rec["line2"].get("expiration_date", ""),
            "personal_number": rec["line2"].get("personal_number", "")
        })

    # 3) pre‑encode every record once (outside timing)
    encoded_lines = [encode_mrz(f) for f in fields_list]

    # 4) choose your k’s
    ks = [100] + list(range(1000, 10001, 1000))

    # detect mode
    mode = "with_tests" if __debug__ else "without_tests"
    out_csv = f"timings_{mode}.csv"

    # 5) time and write CSV
    with open(out_csv, "w", newline="") as csvf:
        w = csv.writer(csvf)
        w.writerow(["n_records", "encode_s", "decode_s"])
        for k in ks:
            t_e = time_encode(fields_list, k)
            t_d = time_decode(encoded_lines, k)
            w.writerow([k, f"{t_e:.6f}", f"{t_d:.6f}"])
            print(f"[{mode}] k={k:5d} → encode {t_e:.6f}s, decode {t_d:.6f}s")

    print(f"Done: wrote {out_csv}")

if __name__ == "__main__":
    main()
