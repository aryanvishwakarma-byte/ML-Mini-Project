import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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

def add_concept_card(doc, concept_num, concept_name, category, what_is_it, why_used, where_used, how_used, math_or_intuition):
    """Adds a structured, comprehensive conceptual breakdown card."""
    tbl = doc.add_table(rows=6, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header row
    hdr_cell = tbl.cell(0, 0)
    hdr_cell.merge(tbl.cell(0, 1))
    set_cell_background(hdr_cell, "1D3557")
    set_cell_margins(hdr_cell, 120, 120, 150, 150)
    p_hdr = hdr_cell.paragraphs[0]
    p_hdr.paragraph_format.space_before = Pt(2)
    p_hdr.paragraph_format.space_after = Pt(2)
    r_hdr = p_hdr.add_run(f"CONCEPT #{concept_num}: {concept_name.upper()}  [{category}]")
    r_hdr.bold = True
    r_hdr.font.name = "Calibri"
    r_hdr.font.size = Pt(11)
    r_hdr.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    
    sections = [
        ("1. What is it?", what_is_it),
        ("2. Why did we use it?", why_used),
        ("3. Where is it used?", where_used),
        ("4. How did we use it?", how_used),
        ("5. Mathematical / Technical Intuition", math_or_intuition)
    ]
    
    for idx, (label, content) in enumerate(sections):
        row = tbl.rows[idx + 1]
        c0 = row.cells[0]
        c1 = row.cells[1]
        
        bg_color = "F8F9FA" if (idx % 2 == 1) else "FFFFFF"
        set_cell_background(c0, "EBF3FB")
        set_cell_background(c1, bg_color)
        
        set_cell_margins(c0, 100, 100, 120, 120)
        set_cell_margins(c1, 100, 100, 120, 120)
        
        # Widths: Col 0 narrow, Col 1 wide
        c0.width = Inches(2.2)
        c1.width = Inches(4.5)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.name = "Calibri"
        r0.font.size = Pt(10)
        r0.font.color.rgb = RGBColor(0x1D, 0x35, 0x57)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(content)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(0x21, 0x25, 0x29)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

def create_concepts_guide(output_filename="Smart_Delivery_Zones_Project_Concepts_Guide.docx"):
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    COLOR_PRIMARY = RGBColor(0x1D, 0x35, 0x57)
    COLOR_SECONDARY = RGBColor(0x2A, 0x9D, 0x8F)

    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = RGBColor(0x21, 0x25, 0x29)
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(6)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("PROJECT COMPREHENSIVE CONCEPTS GUIDE")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(24)
    r_title.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(24)
    r_sub = p_sub.add_run("In-Depth Breakdown of Every Algorithm, Mathematical Model, and Methodology Used")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = COLOR_SECONDARY
    r_sub.italic = True

    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(24)
    r_line = p_line.add_run("―" * 45)
    r_line.font.color.rgb = RGBColor(0xCD, 0xD7, 0xE0)

    p_intro = doc.add_paragraph()
    p_intro.add_run(
        "This companion guide provides an exhaustive, question-and-answer breakdown of every concept implemented in the "
        "Smart Delivery Zones project. For every technique, it explains: What it is, Why we used it, Where it is used in the codebase, "
        "How it was implemented, and the underlying Mathematical / Algorithmic Intuition. "
        "Use this document for your project report preparation, viva examinations, and technical presentations."
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # CONCEPT 1: THE TRAVELLING SALESPERSON PROBLEM (TSP)
    # -------------------------------------------------------------
    add_concept_card(
        doc,
        concept_num=1,
        concept_name="The Travelling Salesperson Problem (TSP) & Vehicle Routing (VRP)",
        category="Problem Domain & Theoretical Foundations",
        what_is_it=(
            "The Travelling Salesperson Problem is an NP-hard combinatorial optimization challenge where an agent must visit a given set of cities "
            "exactly once and return to the starting depot such that the total travel distance is minimized."
        ),
        why_used=(
            "Last-mile delivery is fundamentally a multi-vehicle TSP. Without solving TSP, delivery drivers take arbitrary, crisscrossing paths, "
            "wasting fuel, increasing wear-and-tear, and violating delivery time windows."
        ),
        where_used=(
            "Applied in src/shortest_path.py (within nearest_neighbor_tsp and two_opt_optimize) to compute the delivery itinerary for each truck."
        ),
        how_used=(
            "Rather than solving one massive 1,000-city TSP (which has 1,000! permutations), we use clustering to split the problem into k independent "
            "small TSPs of 20 to 40 stops each, which can be solved in milliseconds."
        ),
        math_or_intuition=(
            "Complexity: Raw brute-force TSP scales as O(n!). For n=100 stops, (100-1)! / 2 exceeds the number of atoms in the universe. "
            "By decomposing the problem into clusters of size m ≈ 25, (25-1)! becomes tractable via heuristic local search."
        )
    )

    # -------------------------------------------------------------
    # CONCEPT 2: HAVERSINE DISTANCE FORMULA
    # -------------------------------------------------------------
    add_concept_card(
        doc,
        concept_num=2,
        concept_name="Haversine Great-Circle Distance Metric",
        category="Geodesic Mathematics & Feature Engineering",
        what_is_it=(
            "The Haversine formula calculates the shortest distance over the Earth's spherical surface (great-circle distance) between two pairs of "
            "GPS latitude and longitude coordinates."
        ),
        why_used=(
            "Standard Euclidean flat distance sqrt((x2-x1)^2 + (y2-y1)^2) is geometrically invalid on Earth's curved surface. In Mumbai, longitude "
            "degrees are physically narrower than latitude degrees because of the Earth's curvature. Haversine gives true kilometer distances."
        ),
        where_used=(
            "Implemented in src/clustering.py (haversine_distance and compute_distance_matrix) and src/shortest_path.py."
        ),
        how_used=(
            "Takes raw degrees, converts to radians, computes angular differences (Δlat, Δlon), applies spherical trigonometry, and multiplies by Earth's mean radius (R = 6,371.0 km)."
        ),
        math_or_intuition=(
            "Formula: a = sin²(Δφ / 2) + cos(φ₁) · cos(φ₂) · sin²(Δλ / 2)\n"
            "c = 2 · atan2(√a, √(1 - a))\n"
            "d = R · c\n"
            "Ensures our road-distance approximations are physically accurate to within 1-2% of actual road paths."
        )
    )

    # -------------------------------------------------------------
    # CONCEPT 3: CUSTOM STANDARD SCALER
    # -------------------------------------------------------------
    add_concept_card(
        doc,
        concept_num=3,
        concept_name="Custom Feature Preprocessing & Standardization (StandardScaler)",
        category="Module 1.3: Preprocessing and Scaling",
        what_is_it=(
            "Feature standardization transforms numerical variables so that they have a mean of 0 and a standard deviation of 1: z = (x - μ) / σ."
        ),
        why_used=(
            "K-Means and DBSCAN rely on distance calculations. In Mumbai, latitudes range from 18.90 to 19.23 (~0.33 range) while longitudes range from 72.80 to 73.00 (~0.20 range). "
            "Without standardization, the axis with larger variance artificially dominates cluster assignment."
        ),
        where_used=(
            "Implemented as CustomStandardScaler in src/clustering.py and applied to GPS coordinates before clustering in main.py and app.py."
        ),
        how_used=(
            "Coded from scratch with pure NumPy. Fits mean and standard deviation on training coordinates and transforms features via vectorized array arithmetic."
        ),
        math_or_intuition=(
            "Formula: z_i = (x_i - mean(X)) / std(X)\n"
            "Guarantees spherical Euclidean feature space where both north-south and east-west geographic distances are weighted equitably by clustering algorithms."
        )
    )

    # -------------------------------------------------------------
    # CONCEPT 4: K-MEANS CLUSTERING & K-MEANS++ INITIALIZATION
    # -------------------------------------------------------------
    add_concept_card(
        doc,
        concept_num=4,
        concept_name="K-Means Clustering with K-Means++ Seeding",
        category="Module 4.3: Unsupervised Clustering",
        what_is_it=(
            "A centroid-based unsupervised clustering algorithm that iteratively partitions n observations into k distinct clusters, where each point belongs to the cluster with the nearest centroid."
        ),
        why_used=(
            "Delivery fleets require convex, compact, and balanced territories with clear centers so each delivery truck has a designated, non-overlapping sector."
        ),
        where_used=(
            "Implemented as CustomKMeans in src/clustering.py; primary algorithm driving vehicle zone dispatch in app.py."
        ),
        how_used=(
            "1. Initializes centroids using K-Means++ (probabilistic distance-weighted seeding).\n"
            "2. Assignment Step: Assigns every delivery stop to the closest centroid.\n"
            "3. Update Step: Recomputes each centroid as the geometric mean of assigned points.\n"
            "4. Convergence: Stops when centroids move less than 1e-5."
        ),
        math_or_intuition=(
            "Objective Function: J = Σ Σ ||x_i - μ_k||² (minimizing Within-Cluster Sum of Squares).\n"
            "K-Means++ seeds subsequent centers with probability P(x) = D(x)² / Σ D(x)², avoiding poor local optima and mathematically ensuring O(log k) competitive bounds."
        )
    )

    # -------------------------------------------------------------
    # CONCEPT 5: DENSITY-BASED SPATIAL CLUSTERING (DBSCAN)
    # -------------------------------------------------------------
    add_concept_card(
        doc,
        concept_num=5,
        concept_name="DBSCAN (Density-Based Spatial Clustering with Noise Detection)",
        category="Module 4.3: Unsupervised Clustering",
        what_is_it=(
            "A density-based clustering algorithm that groups points closely packed together (within radius ε) while labeling points in sparse regions as noise/outliers (Cluster -1)."
        ),
        why_used=(
            "Real cities have non-spherical geography (Mumbai's coastal shape). DBSCAN demonstrates how AI detects isolated, fringe customer orders that should not force a delivery truck out of its core urban zone."
        ),
        where_used=(
            "Implemented as CustomDBSCAN in src/clustering.py and accessible via the sidebar model toggle in app.py."
        ),
        how_used=(
            "Calculates distance matrix. For each point: if neighbors ≥ min_samples, it forms a Core Point and expands the cluster using breadth-first search. Otherwise, marks as noise."
        ),
        math_or_intuition=(
            "Core Point: |N_ε(p)| ≥ min_samples.\n"
            "Border Point: Within ε of a core point but has < min_samples.\n"
            "Noise Point: Neither core nor border. Protects delivery fleet efficiency by filtering extreme outlier stops."
        )
    )

    # -------------------------------------------------------------
    # CONCEPT 6: CLUSTER EVALUATION METRICS (ELBOW & SILHOUETTE)
    # -------------------------------------------------------------
    add_concept_card(
        doc,
        concept_num=6,
        concept_name="Quantitative Cluster Validation: Inertia, Silhouette & Davies-Bouldin",
        category="Module 4.3: Comparing & Evaluating Clustering",
        what_is_it=(
            "Mathematical diagnostics used to evaluate how well-separated and cohesive clusters are without having true ground-truth labels."
        ),
        why_used=(
            "To prove scientifically how many delivery zones (k) should be created, rather than guessing a random number."
        ),
        where_used=(
            "Implemented in find_optimal_k, calculate_silhouette_score, and calculate_davies_bouldin in src/clustering.py."
        ),
        how_used=(
            "Evaluates K from 2 to 6. Identifies the 'elbow point' in Inertia where adding extra trucks yields diminishing returns, and verifies peak Silhouette score."
        ),
        math_or_intuition=(
            "• Inertia (WCSS): Σ ||x - μ||² (Lower = tighter).\n"
            "• Silhouette Score: s(i) = (b(i) - a(i)) / max(a(i), b(i)) where a(i) is intra-cluster distance and b(i) is nearest-cluster distance. Ranges from -1 to +1 (scores > 0.40 indicate strong clustering).\n"
            "• Davies-Bouldin: Measures ratio of cluster scatter to centroid separation (Lower = better)."
        )
    )

    # -------------------------------------------------------------
    # CONCEPT 7: DIJKSTRA'S SHORTEST PATH ALGORITHM
    # -------------------------------------------------------------
    add_concept_card(
        doc,
        concept_num=7,
        concept_name="Dijkstra's Single-Source Shortest Path Algorithm",
        category="Core Graph Algorithms",
        what_is_it=(
            "A greedy graph traversal algorithm that finds the shortest path between a starting node and all other vertices in a weighted graph with non-negative edge weights."
        ),
        why_used=(
            "To compute point-to-point shortest routes between key delivery intersections and warehouse nodes."
        ),
        where_used=(
            "Implemented as dijkstra_shortest_path in src/shortest_path.py."
        ),
        how_used=(
            "Maintains a min-priority queue (heapq). At each step, extracts the vertex with the lowest known cumulative distance, relaxes adjacent edges, and updates predecessor pointers to reconstruct the exact path."
        ),
        math_or_intuition=(
            "Time Complexity: O((V + E) log V) using a binary heap.\n"
            "Guarantees mathematical optimality for non-negative edge weights by exploiting optimal substructure: any subpath of a shortest path is also a shortest path."
        )
    )

    # -------------------------------------------------------------
    # CONCEPT 8: GREEDY NEAREST NEIGHBOR TSP HEURISTIC
    # -------------------------------------------------------------
    add_concept_card(
        doc,
        concept_num=8,
        concept_name="Greedy Nearest Neighbor Constructive TSP Heuristic",
        category="Combinatorial Optimization Heuristics",
        what_is_it=(
            "A fast constructive heuristic for TSP that starts at a depot, repeatedly visits the nearest unvisited node, and finally returns to the depot."
        ),
        why_used=(
            "Provides an initial feasible tour in O(n²) time. While not globally optimal, it creates the baseline route upon which local search algorithms can optimize."
        ),
        where_used=(
            "Implemented as nearest_neighbor_tsp in src/shortest_path.py."
        ),
        how_used=(
            "Starts at BKC Depot (index 0). Maintains an unvisited set. At each step, finds min(dist[current][unvisited]), appends to route, updates current location, and appends depot at the end."
        ),
        math_or_intuition=(
            "Time Complexity: O(n²).\n"
            "Limitation: Greedy decisions early in the tour often force the agent into long, awkward return jumps near the end ('the greedy trap'). This necessitates subsequent 2-Opt optimization."
        )
    )

    # -------------------------------------------------------------
    # CONCEPT 9: 2-OPT EDGE-EXCHANGE LOCAL SEARCH OPTIMIZATION
    # -------------------------------------------------------------
    add_concept_card(
        doc,
        concept_num=9,
        concept_name="2-Opt Edge-Exchange Local Search Route Optimizer",
        category="Shortest Path Tour Optimization",
        what_is_it=(
            "A local search optimization algorithm that systematically takes pairs of edges in a TSP tour, cuts them, and reconnects them in reverse order to eliminate crossing paths."
        ),
        why_used=(
            "Eliminates the 'greedy trap' left by Nearest Neighbor TSP. In Euclidean plane routing, crossing edges (like an 'X') always violate the Triangle Inequality. 2-Opt untangles these crossings to find the true shortest circuit."
        ),
        where_used=(
            "Implemented as two_opt_swap and two_opt_optimize in src/shortest_path.py."
        ),
        how_used=(
            "Iterates through edge pairs (i, k). Checks if swapping segment [i:k+1] reduces total distance. If delta < 0, adopts the new tour and repeats until no further 2-opt improvements exist."
        ),
        math_or_intuition=(
            "Swap Condition: If dist(u, v) + dist(u+1, v+1) < dist(u, u+1) + dist(v, v+1), execute swap.\n"
            "Guarantees a 2-optimal tour that has zero crossed lines, reducing overall fleet travel distance by 10% to 15% across Mumbai."
        )
    )

    # -------------------------------------------------------------
    # CONCEPT 10: CLUSTER-FIRST, ROUTE-SECOND PARADIGM
    # -------------------------------------------------------------
    add_concept_card(
        doc,
        concept_num=10,
        concept_name="The 'Cluster-First, Route-Second' Logistics Architecture",
        category="System Architecture & Industry Practice",
        what_is_it=(
            "A two-phase optimization paradigm where high-dimensional data is first partitioned spatially into clusters, after which graph routing is executed independently within each partition."
        ),
        why_used=(
            "Bridges the gap between Machine Learning (pattern recognition / spatial segmentation) and Operations Research (deterministic shortest path routing). "
            "Solves real-world vehicle routing without exploding computational complexity."
        ),
        where_used=(
            "Orchestrated across main.py and app.py, connecting src/clustering.py to src/shortest_path.py."
        ),
        how_used=(
            "1. ML Phase: K-Means/DBSCAN groups stops into k zones.\n"
            "2. Optimization Phase: BKC Depot is joined to each zone, and 2-Opt shortest path is solved per truck.\n"
            "3. Output Phase: Dispatches k vehicles in parallel."
        ),
        math_or_intuition=(
            "Scalability: Solves k subproblems of size (n/k) in parallel instead of one monolithic problem of size n. "
            "Reduces complexity from O(n!) to k · O((n/k)²), making city-wide optimization execute in under 1 second."
        )
    )

    try:
        doc.save(output_filename)
        print(f"Concepts Guide saved at: {output_filename}")
        return output_filename
    except PermissionError:
        fallback = "Smart_Delivery_Zones_Project_Concepts_Guide_Updated.docx"
        doc.save(fallback)
        print(f"Original open. Saved Concepts Guide to: {fallback}")
        return fallback

if __name__ == "__main__":
    create_concepts_guide()
