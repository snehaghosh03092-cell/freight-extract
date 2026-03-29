def build_prompt(email_id, subject, body, ports):
      return f"""
          You are a freight email information extraction system.
          Your task is to extract structured shipment data from an email.
            ========================
            VALID PORT LIST
            ========================
            Use the following port reference list:

            {ports}

            - Prefer ports from this list
            - If exact port is not found, use the closest match
            - If only country is known → set port_code = null and use country as port_name

              ========================
              INPUT
              ========================

              EMAIL ID: {email_id}

              Subject:
              {subject}

              Body:
              {body}

              ========================
              OUTPUT FORMAT (STRICT)
              ========================

              Return ONLY valid JSON:

              {{
                "id": string,
                "product_line": string,
                "incoterm": string,
                "origin_port_code": string or null,
                "origin_port_name": string or null,
                "destination_port_code": string or null,
                "destination_port_name": string or null,
                "cargo_weight_kg": number or null,
                "cargo_cbm": number or null,
                "is_dangerous": boolean
              }}

              ========================
              CORE RULES
              ========================

              1. SOURCE PRIORITY
              - Use BODY first
              - Use SUBJECT only if needed

              2. ROUTE EXTRACTION
              - Extract origin (POL) and destination (POD)
              - If ICD is present → prefer ICD as destination
              - If multiple routes → take FIRST route only

              3. ORIGIN INFERENCE
              If origin is missing:
              - Infer from context (e.g., "Japanese goods" → Japan)
              - Map adjectives:
                Japanese → Japan
                Chinese → China
                Korean → Korea
                Thai → Thailand

              4. PORT HANDLING
              - Never invent ports
              - If port code exists → map to name using list
              - If only country known → port_code = null

              5. PRODUCT LINE
              - Destination starts with "IN" → pl_sea_import_lcl
              - Origin starts with "IN" → pl_sea_export_lcl

              6. INCOTERM
              - Recognize these incoterms (normalize to uppercase): `FOB`, `CIF`, `CFR`, `EXW`, `DDP`, `DAP`, `FCA`, `CPT`, `CIP`, `DPU`
              - Default = FOB
              - Always uppercase

              7. CARGO EXTRACTION

              Extract independently:

              WEIGHT:
              - kg → use as-is
              - lbs → × 0.453592
              - ton / MT → × 1000

              VOLUME:
              - cbm → use as-is
              - RT → 
                cargo_cbm = value
                cargo_weight_kg = value × 1000

              - If both present → keep both
              - Round to max 2 decimals
              - Do NOT force trailing zeros

              8. DANGEROUS GOODS
              - TRUE if: DG, hazardous, IMO, IMDG, Class 1–9
              - FALSE otherwise

              9. NULL RULE
              - Missing values → null
              - NEVER empty string

              10. BOOLEAN RULE
              - is_dangerous must ALWAYS be true or false

              ========================
              EXAMPLES
              ========================

              Example 1:

              INPUT:
              "Shipment from Shanghai to Mundra ICD, 2 CBM"

              OUTPUT:
              {{
                "id": "EMAIL_001",
                "product_line": "pl_sea_import_lcl",
                "incoterm": "FOB",
                "origin_port_code": "CNSHA",
                "origin_port_name": "Shanghai",
                "destination_port_code": "INMUN",
                "destination_port_name": "Mundra ICD",
                "cargo_weight_kg": null,
                "cargo_cbm": 2,
                "is_dangerous": false
              }}

              Example 2:

              INPUT:
              "Japanese goods to Chennai, 500 kg"

              OUTPUT:
              {{
                "id": "EMAIL_002",
                "product_line": "pl_sea_import_lcl",
                "incoterm": "FOB",
                "origin_port_code": null,
                "origin_port_name": "Japan",
                "destination_port_code": "INMAA",
                "destination_port_name": "Chennai",
                "cargo_weight_kg": 500,
                "cargo_cbm": null,
                "is_dangerous": false
              }}

              Example 3:

              INPUT:
              "DG cargo 2 RT from Busan to Nhava Sheva"

              OUTPUT:
              {{
                "id": "EMAIL_003",
                "product_line": "pl_sea_import_lcl",
                "incoterm": "FOB",
                "origin_port_code": "KRPUS",
                "origin_port_name": "Busan",
                "destination_port_code": "INNSA",
                "destination_port_name": "Nhava Sheva",
                "cargo_weight_kg": 2000,
                "cargo_cbm": 2,
                "is_dangerous": true
              }}

              ========================
              FINAL INSTRUCTION
              ========================

              - Output ONLY JSON
              - No explanation
              - No markdown
              - No extra text
              """