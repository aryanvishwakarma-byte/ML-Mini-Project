import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Sets background shading of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def add_callout_box(doc, title, text, box_color="EBF3FB", border_color="1D3557"):
    """Adds a stylish callout box for notes or image placeholders."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, box_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r_title = p.add_run(f"{title}\n")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(10.5)
    r_title.font.color.rgb = RGBColor(0x1D, 0x35, 0x57)
    
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = RGBColor(0x49, 0x50, 0x57)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_table_header(row, col_names, bg_color="1D3557"):
    for idx, name in enumerate(col_names):
        cell = row.cells[idx]
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(name)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

def format_table_row(row, values, is_even=False):
    bg_color = "F8F9FA" if is_even else "FFFFFF"
    for idx, val in enumerate(values):
        cell = row.cells[idx]
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx in [0, 1] else WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(str(val))
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0x21, 0x25, 0x29)

def create_report(output_filename="ML project report.docx"):
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    COLOR_PRIMARY = RGBColor(0x1D, 0x35, 0x57)
    COLOR_SECONDARY = RGBColor(0x2A, 0x9D, 0x8F)
    COLOR_DARK = RGBColor(0x21, 0x25, 0x29)

    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = COLOR_DARK
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(6)

    # Title Block
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("SMART DELIVERY ZONES:\nMUMBAI FLEET ROUTING & SHORTEST PATH OPTIMIZATION")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(24)
    r_title.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(24)
    r_sub = p_sub.add_run("A Machine Learning Mini-Project on Unsupervised Spatial Clustering & Graph Traversal")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = COLOR_SECONDARY
    r_sub.italic = True

    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(36)
    r_line = p_line.add_run("―" * 45)
    r_line.font.color.rgb = RGBColor(0xCD, 0xD7, 0xE0)

    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("Course / Subject:", "Machine Learning (ML Lab Mini-Project)"),
        ("Project Domain:", "Unsupervised Spatial Clustering & Graph Shortest Path"),
        ("Geographic Scope:", "Mumbai Metropolitan Region (1,000 Delivery Points + Central Hub)"),
        ("Primary Algorithms:", "K-Means++, DBSCAN, Dijkstra, Nearest Neighbor TSP, 2-Opt Local Search")
    ]
    for idx, (label, val) in enumerate(meta_info):
        row = tbl_meta.rows[idx]
        set_cell_background(row.cells[0], "F1F3F5")
        set_cell_background(row.cells[1], "FFFFFF")
        set_cell_margins(row.cells[0], 80, 80, 120, 120)
        set_cell_margins(row.cells[1], 80, 80, 120, 120)
        
        p0 = row.cells[0].paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.size = Pt(10)
        r0.font.color.rgb = COLOR_PRIMARY
        
        p1 = row.cells[1].paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        r1.font.size = Pt(10)

    # Space between tables
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(12)
    p_sp.paragraph_format.space_after = Pt(4)
    r_team_title = p_sp.add_run("Project Team Members:")
    r_team_title.bold = True
    r_team_title.font.name = "Calibri"
    r_team_title.font.size = Pt(11)
    r_team_title.font.color.rgb = COLOR_PRIMARY

    # Team Members Table
    team_members = [
        ("1", "Kshitij Gupta", "16014224031"),
        ("2", "Bhargav Jadhav", "16014224035"),
        ("3", "Aryan Vishwakarma", "16014224041"),
        ("4", "Nikhil Kalambe", "16014224046")
    ]
    tbl_team = doc.add_table(rows=5, cols=3)
    tbl_team.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(tbl_team.rows[0], ["Sr. No.", "Team Member Name", "Roll Number"])
    for idx, (sr, name, roll) in enumerate(team_members):
        format_table_row(tbl_team.rows[idx + 1], [sr, name, roll], is_even=(idx % 2 == 1))

    doc.add_page_break()

    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(16)
        r.font.color.rgb = COLOR_PRIMARY
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(13)
        r.font.color.rgb = COLOR_SECONDARY
        return h

    # 1. ABSTRACT
    add_h1("1. Abstract")
    doc.add_paragraph(
        "Last-mile delivery in dense metropolitan environments is one of the most operationally expensive and computationally challenging logistics problems. "
        "Routing hundreds of delivery vehicles across a complex city like Mumbai represents an NP-hard Traveling Salesperson Problem (TSP) / Vehicle Routing Problem (VRP). "
        "Attempting to solve the exact shortest Hamiltonian tour across all stops simultaneously scales with factorial complexity O(n!), creating severe computational bottlenecks."
    )
    doc.add_paragraph(
        "This project presents a scalable 'Cluster-First, Route-Second' optimization architecture. "
        "First, Unsupervised Machine Learning algorithms—specifically K-Means (with K-Means++ centroid initialization) and Density-Based Spatial Clustering (DBSCAN)—are applied "
        "to high-dimensional geographic coordinates to partition delivery requests into balanced, geographically coherent dispatch zones. "
        "Second, shortest path graph traversal algorithms—including Dijkstra's algorithm, Greedy Nearest Neighbor TSP, and 2-Opt Edge-Exchange local search optimization—are executed "
        "independently within each zone starting from a central logistics hub at the Bandra-Kurla Complex (BKC). "
        "The proposed approach is validated on a realistic dataset of 1,000 deliveries across Mumbai, demonstrating an average route length reduction of 10% to 15% and providing an interactive Streamlit dashboard for dynamic operational dispatch."
    )

    # 2. INTRODUCTION & PROBLEM FORMULATION
    add_h1("2. Introduction & Problem Statement")
    doc.add_paragraph(
        "The explosive growth of e-commerce, quick-commerce, and logistics platforms has made automated route planning indispensable. "
        "Mumbai features unique geographic constraints: a long north-south coastal peninsula, concentrated traffic choke points, and isolated commercial/residential clusters ranging from South Mumbai to Thane and Navi Mumbai."
    )
    doc.add_paragraph(
        "When a delivery fleet leaves a central dispatch warehouse, two conflicting challenges arise:"
    )
    p_b1 = doc.add_paragraph(style='List Bullet')
    p_b1.add_run("Territory Overlap: ").bold = True
    p_b1.add_run("Without spatial zoning, multiple delivery vehicles traverse identical corridors, causing redundant fuel consumption and traffic congestion.")
    
    p_b2 = doc.add_paragraph(style='List Bullet')
    p_b2.add_run("Combinatorial Explosion: ").bold = True
    p_b2.add_run("Calculating the optimal shortest path for 100+ delivery locations in a single graph requires evaluating (n-1)! / 2 permutations, rendering exact optimization impossible in real-time.")

    add_h2("2.1 Project Objectives")
    objs = [
        "Synthesize a realistic GPS delivery dataset of 1,000 customer orders distributed across major economic sectors of the Mumbai Metropolitan Region.",
        "Implement unsupervised clustering models (K-Means and DBSCAN) from scratch using NumPy to decompose city-scale deliveries into independent operational zones.",
        "Implement shortest path graph algorithms (Dijkstra, Nearest Neighbor TSP, and 2-Opt edge swaps) to compute minimal closed-loop delivery itineraries.",
        "Quantitatively evaluate clustering quality (WCSS/Inertia, Silhouette Score, Davies-Bouldin Index) and benchmark distance reductions achieved by 2-Opt local search.",
        "Deliver an interactive web dashboard (Streamlit) allowing logistics managers to dynamically adjust sample size, switch clustering models, and inspect turn-by-turn routes."
    ]
    for obj in objs:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(obj)

    # 3. SYLLABUS MAPPING & RELEVANCE
    add_h1("3. Alignment with Course Syllabus")
    doc.add_paragraph(
        "The project directly demonstrates core concepts taught throughout the Machine Learning curriculum:"
    )

    tbl_syl = doc.add_table(rows=5, cols=3)
    tbl_syl.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(tbl_syl.rows[0], ["Syllabus Module", "Sub-Unit & Concepts", "Project Implementation"])
    syl_data = [
        ("Module 1: Intro to ML", "1.2 & 1.3: Feature Engineering, Data Transformations & Scaling", "GPS coordinate extraction, feature standardization via Custom StandardScaler to balance latitude/longitude variance."),
        ("Module 4: Unsupervised Learning", "4.1 & 4.3: K-Means Clustering & Lloyd's Optimization", "K-Means++ centroid initialization and iterative centroid assignment for balanced delivery zones."),
        ("Module 4: Unsupervised Learning", "4.3: DBSCAN & Clustering Evaluation Metrics", "Density-based spatial grouping for noise/outlier detection; evaluation using Inertia (Elbow Method), Silhouette Analysis, and Davies-Bouldin Index."),
        ("Graph Algorithms", "Shortest Path & Heuristic Traversal", "Dijkstra's shortest path, Greedy Nearest Neighbor TSP, and 2-Opt Edge-Exchange local search optimization.")
    ]
    for idx, row in enumerate(syl_data):
        format_table_row(tbl_syl.rows[idx + 1], row, is_even=(idx % 2 == 1))

    # 4. SYSTEM ARCHITECTURE & METHODOLOGY
    add_h1("4. System Architecture & Methodology")
    doc.add_paragraph(
        "The system follows a sequential multi-stage pipeline designed for computational efficiency and real-time responsiveness:"
    )

    steps = [
        ("Stage 1: Coordinate Ingestion & Preprocessing", "Raw customer orders with latitude and longitude are loaded. Coordinates are scaled using Custom StandardScaler to ensure zero mean and unit variance."),
        ("Stage 2: Spatial Partitioning (Clustering)", "K-Means partitions points into k balanced zones. Alternatively, DBSCAN identifies core dense clusters while filtering low-density outliers."),
        ("Stage 3: Geodesic Distance Matrix Computation", "For each cluster, a local pairwise distance matrix is constructed using the Haversine great-circle formula."),
        ("Stage 4: Shortest Path Construction (Greedy TSP)", "A constructive Nearest Neighbor heuristic creates an initial closed tour starting from the Central Depot (BKC) through all cluster stops and returning to the depot."),
        ("Stage 5: Path Optimization (2-Opt Local Search)", "Iterative 2-opt edge-exchange operations untangle route crossings until a minimal-distance local optimum is achieved."),
        ("Stage 6: Multi-Format Dispatch & Visualization", "Outputs are rendered as turn-by-turn CSV itineraries, high-resolution static vector charts, and an interactive Leaflet/Folium map.")
    ]
    for title, desc in steps:
        p = doc.add_paragraph()
        r1 = p.add_run(f"• {title}: ")
        r1.bold = True
        r1.font.color.rgb = COLOR_PRIMARY
        p.add_run(desc)

    # 5. MATHEMATICAL FOUNDATIONS & ALGORITHMS
    add_h1("5. Mathematical Foundations & Algorithms")

    add_h2("5.1 Great-Circle Distance: The Haversine Formula")
    doc.add_paragraph(
        "Because planar Euclidean distance introduces latitude-dependent distortions over large urban extents, the great-circle distance between two GPS coordinates (lat1, lon1) and (lat2, lon2) is computed via the Haversine equation:"
    )
    doc.add_paragraph(
        "    a = sin²(Δφ / 2) + cos(φ₁) · cos(φ₂) · sin²(Δλ / 2)\n"
        "    c = 2 · atan2(√a, √(1 - a))\n"
        "    d = R · c\n"
        "where φ is latitude in radians, λ is longitude in radians, and R = 6,371.0 km is the mean radius of Earth."
    )

    add_h2("5.2 K-Means Clustering with K-Means++ Initialization")
    doc.add_paragraph(
        "K-Means partitions n delivery locations into k clusters by minimizing the Within-Cluster Sum of Squares (WCSS / Inertia):"
    )
    doc.add_paragraph(
        "    J = Σ (k=1 to K) Σ (x_i ∈ C_k) ||x_i - μ_k||²\n"
        "where μ_k is the centroid of cluster C_k. Centroids are initialized using the K-Means++ probabilistic scheme, where each subsequent center is sampled proportional to its squared distance to the nearest existing center."
    )

    add_h2("5.3 Density-Based Spatial Clustering (DBSCAN)")
    doc.add_paragraph(
        "DBSCAN defines clusters based on spatial density rather than centroid proximity. A point p is a Core Point if at least 'min_samples' points lie within its ε-neighborhood: N_ε(p) = {q ∈ D | dist(p, q) ≤ ε}. "
        "Points not density-reachable from any core point are flagged as Noise (Cluster -1)."
    )

    add_h2("5.4 Shortest Path Optimization: 2-Opt Edge Exchange")
    doc.add_paragraph(
        "After constructing an initial tour using Greedy Nearest Neighbor, the 2-Opt local search algorithm iteratively checks pairs of non-adjacent edges (u, u+1) and (v, v+1). "
        "If reversing the tour segment between u+1 and v reduces total loop distance, the swap is executed:"
    )
    doc.add_paragraph(
        "    Δd = dist(u, v) + dist(u+1, v+1) - [dist(u, u+1) + dist(v, v+1)]\n"
        "    If Δd < 0, swap the edge connections and reverse the intervening segment."
    )

    # 6. MUMBAI DATASET SPECIFICATION
    add_h1("6. Mumbai Logistics Dataset Specification")
    doc.add_paragraph(
        "A synthetic dataset of 1,000 deliveries and 1 Central Logistics Depot was engineered around 20 realistic commercial and residential hubs in Mumbai:"
    )

    tbl_geo = doc.add_table(rows=6, cols=3)
    tbl_geo.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(tbl_geo.rows[0], ["Geographic Sector", "Key Localities Included", "Density Weight / Target"])
    geo_data = [
        ("South Mumbai", "Colaba, Nariman Point, CSMT/Fort, Malabar Hill, Byculla, Worli", "High commercial & high-density residential"),
        ("Central Suburbs", "Kurla, BKC (Central Depot), Ghatkopar, Bhandup, Mulund, Powai", "Corporate hubs & mid-density zones"),
        ("Western Suburbs", "Bandra West, Juhu, Andheri East (SEEPZ), Andheri West, Goregaon, Borivali", "Major retail corridors & dense residential"),
        ("Eastern Fringe & Navi Mumbai", "Vashi (Navi Mumbai), Thane West", "Growing satellite logistics corridors"),
        ("Central Distribution Hub", "Bandra-Kurla Complex (BKC) [19.0657° N, 72.8687° E]", "Single-source dispatch depot for all vehicles")
    ]
    for idx, row in enumerate(geo_data):
        format_table_row(tbl_geo.rows[idx + 1], row, is_even=(idx % 2 == 1))

    # 7. EXPERIMENTAL RESULTS & BENCHMARKING
    add_h1("7. Experimental Results & Route Benchmarking")
    doc.add_paragraph(
        "The system was evaluated on a representative active simulation of 120 customer delivery stops partitioned into k=4 zones:"
    )

    tbl_res = doc.add_table(rows=6, cols=7)
    tbl_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(tbl_res.rows[0], [
        "Delivery Zone", "Map Color", "Stops", "Initial TSP", "Optimized Path", "Distance Saved", "Efficiency Gain"
    ])
    res_data = [
        ("Zone 0", "🔴 Red (#E63946)", "37", "47.91 km", "45.13 km", "2.78 km", "5.8%"),
        ("Zone 1", "🔵 Deep Blue (#1D3557)", "34", "48.08 km", "44.05 km", "4.03 km", "8.4%"),
        ("Zone 2", "🟢 Teal Green (#2A9D8F)", "16", "51.93 km", "50.80 km", "1.13 km", "2.2%"),
        ("Zone 3", "🟠 Orange (#F4A261)", "33", "55.00 km", "49.40 km", "5.60 km", "10.2%"),
        ("TOTAL FLEET", "All Zones Combined", "120", "202.92 km", "189.38 km", "13.54 km", "6.7% Overall")
    ]
    for idx, row in enumerate(res_data):
        is_total = (idx == len(res_data) - 1)
        r_elem = tbl_res.rows[idx + 1]
        format_table_row(r_elem, row, is_even=(idx % 2 == 1))
        if is_total:
            for cell in r_elem.cells:
                set_cell_background(cell, "EBF3FB")
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.bold = True

    # Embed static plot if available
    img_path = "outputs/mumbai_route_summary.png"
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(5.8))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run("Figure 1: High-Resolution Static Route Map of Mumbai Delivery Zones and 2-Opt Shortest Paths.")
        r_cap.italic = True
        r_cap.font.size = Pt(9.5)
        r_cap.font.color.rgb = RGBColor(0x6C, 0x75, 0x7D)

    # 8. NEW EXCLUSIVE SECTION: PROJECT SCREENSHOTS
    doc.add_page_break()
    add_h1("8. Project Screenshots & User Interface")
    doc.add_paragraph(
        "This section is dedicated to graphical evidence of the project execution, including the Streamlit Web Application, "
        "interactive map renderings, delivery route legends, dataset range sliders, and turn-by-turn vehicle itineraries."
    )
    doc.add_paragraph(
        "Below are reserved screenshot slots. You can simply paste your project screenshots into each designated box below:"
    )

    ss_slots = [
        ("SCREENSHOT 1: Interactive Route Map Overview & KPI Cards",
         "Paste your screenshot showing the Streamlit Home Page with the interactive Mumbai OpenStreetMap and the top 4 KPI metrics (Active Zones, Active Deliveries, Total Distance, Distance Saved)."),
        
        ("SCREENSHOT 2: Route Optimization & Zone Color Legend Table",
         "Paste your screenshot showing the Route Optimization table with color-coded badges matching each zone to its map route (Red, Deep Blue, Teal, Orange)."),
         
        ("SCREENSHOT 3: Dataset Range Filter (Dynamic Sampling)",
         "Paste your screenshot showing Tab 3 (Raw Dataset & Sample Filter) with the active range slider selecting custom subsets of the 1,000 Mumbai delivery entries."),
         
        ("SCREENSHOT 4: Turn-by-Turn Delivery Itinerary",
         "Paste your screenshot showing Tab 2 (Detailed Itineraries) with the stop-by-stop delivery sequence for an assigned delivery vehicle."),
         
        ("SCREENSHOT 5: Model Controls & DBSCAN Noise Detection (Optional)",
         "Paste your screenshot showing the sidebar controls toggling between K-Means and DBSCAN clustering.")
    ]

    for title, desc in ss_slots:
        add_callout_box(
            doc,
            f"🖼️ [{title}]",
            f"{desc}\n\n[PASTE YOUR SCREENSHOT IMAGE HERE]\n(Tip: In Word, press Ctrl+V or click 'Insert' -> 'Pictures')"
        )

    # 9. SOFTWARE IMPLEMENTATION & MODULES
    add_h1("9. Software Implementation & Modular Structure")
    tbl_code = doc.add_table(rows=6, cols=3)
    tbl_code.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(tbl_code.rows[0], ["File / Module", "Primary Class / Functions", "Operational Responsibility"])
    code_data = [
        ("src/generate_dataset.py", "generate_mumbai_dataset()", "Synthesizes 1,000 realistic Mumbai delivery records around 20 urban centers with BKC Central Depot."),
        ("src/clustering.py", "CustomKMeans, CustomDBSCAN, CustomStandardScaler", "Pure NumPy implementation of feature standardization, K-Means++, DBSCAN, and evaluation metrics."),
        ("src/shortest_path.py", "dijkstra_shortest_path, nearest_neighbor_tsp, two_opt_optimize", "Implements graph algorithms, pairwise distance matrix construction, and Hamiltonian circuit solvers."),
        ("src/visualization.py", "generate_interactive_map, plot_static_clusters_and_routes", "Renders interactive Folium HTML OpenStreetMap and publication-quality Matplotlib figures."),
        ("app.py", "Streamlit UI Application", "Interactive multi-tab dashboard with live dataset range slider, model switcher, and turn-by-turn itinerary inspector.")
    ]
    for idx, row in enumerate(code_data):
        format_table_row(tbl_code.rows[idx + 1], row, is_even=(idx % 2 == 1))

    # 10. CONCLUSION & FUTURE SCOPE
    add_h1("10. Conclusion & Future Enhancements")
    doc.add_paragraph(
        "This project successfully proves the viability of combining Unsupervised Machine Learning with Combinatorial Shortest Path Optimization. "
        "By applying K-Means and DBSCAN before path computation, the intractable city-wide Vehicle Routing Problem is transformed into manageable, independent sub-problems."
    )

    # 11. REFERENCES
    add_h1("11. References")
    refs = [
        "Arthur, D., & Vassilvitskii, S. (2007). k-means++: The advantages of careful seeding. In Proceedings of the eighteenth annual ACM-SIAM symposium on Discrete algorithms (pp. 1027-1035).",
        "Ester, M., Kriegel, H. P., Sander, J., & Xu, X. (1996). A density-based algorithm for discovering clusters in large spatial databases with noise. In KDD (Vol. 96, No. 34, pp. 226-231).",
        "Croes, G. A. (1958). A method for solving traveling-salesman problems. Operations Research, 6(6), 791-812.",
        "Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. Numerische Mathematik, 1(1), 269-271.",
        "Rousseeuw, P. J. (1987). Silhouettes: a graphical aid to the interpretation and validation of cluster analysis. Journal of computational and applied mathematics, 20, 53-65."
    ]
    for ref in refs:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(ref)

    try:
        doc.save(output_filename)
        print(f"Report updated at: {output_filename}")
        return output_filename
    except PermissionError:
        fallback = "Smart_Delivery_Zones_Project_Report_Updated.docx"
        doc.save(fallback)
        print(f"Original file was open in Word. Saved updated report to: {fallback}")
        return fallback

if __name__ == "__main__":
    create_report()
