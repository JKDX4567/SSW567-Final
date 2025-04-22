import json
from MRTD import encode_mrz

def main():
    with open("records_decoded.json", "r") as f:
        data = json.load(f)

    records = data["records_decoded"]
    output_lines = []

    for record in records:
        name_parts = record["line1"].get("given_name", "").split()
        first_name = name_parts[0] if name_parts else ""
        middle_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        fields = {
            "document_type": "P",
            "issuing_country": record["line1"].get("issuing_country", "")[:3],
            "last_name": record["line1"].get("last_name", ""),
            "first_name": first_name,
            "middle_name": middle_name,
            "passport_number": record["line2"].get("passport_number", ""),
            "country_code": record["line2"].get("country_code", ""),
            "birth_date": record["line2"].get("birth_date", ""),
            "sex": record["line2"].get("sex", ""),
            "expiration_date": record["line2"].get("expiration_date", ""),
            "personal_number": record["line2"].get("personal_number", "")
        }

        line1, line2 = encode_mrz(fields)
        output_lines.append(f"{line1};{line2}")

    with open("records_encoded.json", "w") as f:
        for line in output_lines:
            f.write(line + "\n")

    print(f"Encoded {len(output_lines)} records and saved to records_encoded.json")

if __name__ == "__main__":
    main()
