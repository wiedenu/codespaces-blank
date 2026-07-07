from fpdf import FPDF

class SOP(FPDF):
    def header(self):
        pass
    def footer(self):
        pass

pdf = SOP(orientation='P', unit='mm', format='Letter')
pdf.add_page()
pdf.set_margins(18, 16, 18)
pdf.set_auto_page_break(auto=False)

GREEN = (45, 107, 78)
DARK  = (30, 30, 30)
GRAY  = (90, 90, 90)
LGRAY = (230, 235, 230)

# ── Title ────────────────────────────────────────────────────────────────────
pdf.set_font("Helvetica", "B", 17)
pdf.set_text_color(*GREEN)
pdf.cell(0, 9, "HubSpot Naming SOP", ln=True)
pdf.set_font("Helvetica", "", 10)
pdf.set_text_color(*GRAY)
pdf.cell(0, 5, "FY27  |  Campaign & Asset Naming Standards", ln=True)
pdf.ln(3)

# ── Helper ───────────────────────────────────────────────────────────────────
def section(title):
    pdf.set_fill_color(*GREEN)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, f"  {title}", ln=True, fill=True)
    pdf.set_text_color(*DARK)
    pdf.ln(1)

def label(text):
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*GREEN)
    pdf.cell(0, 5, text, ln=True)
    pdf.set_text_color(*DARK)

def mono(text, indent=6):
    pdf.set_font("Courier", "", 9)
    pdf.set_x(pdf.get_x() + indent)
    pdf.cell(0, 5, text, ln=True)
    pdf.set_font("Helvetica", "", 9)

def body(text, indent=6):
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(pdf.get_x() + indent)
    pdf.multi_cell(0, 5, text)

def bullet(text, indent=8):
    pdf.set_font("Helvetica", "", 9)
    x = pdf.get_x()
    pdf.set_x(x + indent)
    pdf.cell(4, 5, chr(149))   # bullet char
    pdf.multi_cell(0, 5, text)

def rule(text, indent=8):
    pdf.set_font("Helvetica", "", 9)
    x = pdf.get_x()
    pdf.set_x(x + indent)
    pdf.set_text_color(180, 30, 30)
    pdf.cell(4, 5, "!")
    pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 5, text)

def divider():
    pdf.set_draw_color(*LGRAY)
    pdf.line(18, pdf.get_y(), 196, pdf.get_y())
    pdf.ln(2)

# ── CAMPAIGN NAMING ──────────────────────────────────────────────────────────
section("Campaign Naming")
label("Format:")
mono("FY## – [BU] – [Program]")
pdf.ln(1)
label("Examples:")
for ex in ["FY27 – SMG – Tradeshows",
           "FY27 – CTG – Tradeshows",
           "FY27 – OEG – Tradeshows"]:
    mono(ex)
pdf.ln(3)

# ── ASSET NAMING ─────────────────────────────────────────────────────────────
section("Asset Naming")
label("Format:")
mono("[BU] – [Program / Event / Audience] – [Descriptor]")
pdf.ln(1)
label("Examples:")
for ex in ["SMG – CEDIA Expo 2026 – Pre-Event",
           "SMG – CEDIA Expo 2026 – Post-Event Follow-Up",
           "SMG – Yanmar – May 2026",
           "CTG – Marketing Momentum – May 2026",
           "OEG – Cannata Report – 2026 – 01"]:
    mono(ex)
pdf.ln(3)

# ── DESCRIPTORS ──────────────────────────────────────────────────────────────
section("Descriptors  (Use Only These)")

col_w = 43
row_h = 5
x0 = pdf.get_x()

groups = [
    ("Time",         ["Month YYYY", "(e.g., May 2026)"]),
    ("Sequence",     ["01, 02, 03", ""]),
    ("Event Stage",  ["Pre-Event", "On-Site", "Post-Event", "Follow-Up"]),
    ("Purpose",      ["Announcement", "Promotion", "Reminder", "Invitation"]),
]

cols = [[] for _ in range(4)]
for i, (grp, items) in enumerate(groups):
    cols[i].append(("label", grp))
    for it in items:
        cols[i].append(("body", it))

max_rows = max(len(c) for c in cols)
y_start = pdf.get_y()

for row in range(max_rows):
    y = y_start + row * row_h
    for ci, col in enumerate(cols):
        x = 18 + ci * col_w
        pdf.set_xy(x, y)
        if row < len(col):
            kind, text = col[row]
            if kind == "label":
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(*GREEN)
                pdf.cell(col_w, row_h, text)
            else:
                pdf.set_font("Helvetica", "", 8.5)
                pdf.set_text_color(*DARK)
                pdf.cell(col_w, row_h, text)

pdf.set_text_color(*DARK)
pdf.ln(max_rows * row_h + 2)
divider()

# ── RULES ────────────────────────────────────────────────────────────────────
section("Rules  (Non-Negotiable)")
rules = [
    "Do not include asset type (Email, Form, etc.)",
    "No free-form descriptors",
    "Use one consistent event name",
    "Do not mix formats (e.g., May 2026 only, no 05/2026)",
]
for r in rules:
    rule(r)
pdf.ln(2)
divider()

# ── SOCIAL POSTS ─────────────────────────────────────────────────────────────
section("Social Posts")
body("Do not rename social posts. Assign to the correct campaign only.", indent=6)

pdf.output("/workspaces/codespaces-blank/HubSpot_Naming_SOP_FY27.pdf")
print("PDF written.")
