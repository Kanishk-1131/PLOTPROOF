# PlotProof GIS & Spatial Validation Engine

## 1. Objective
Evaluates whether the physical land parcel described in the deed geographically fits within registered cadastral boundaries without encroaching on adjacent plots.

---

## 2. Coordinate Systems & Geodesy
- **Storage & Input CRS:** WGS84 (`EPSG:4326` — Degrees Latitude/Longitude).
- **Metric Computation CRS:** Universal Transverse Mercator (UTM Zone 44N / `EPSG:32644` — Meters) for Tamil Nadu & Southern India.
- **Coordinate Ordering:** Standardized internally as `(Longitude = X, Latitude = Y)`.

---

## 3. Topological Spatial Relationships

| Relationship | Definition | Verification Outcome |
|:---|:---|:---|
| **IDENTICAL** | Candidate polygon exactly matches target cadastral parcel | ✓ PASS |
| **WITHIN** | Candidate polygon lies entirely inside registered parcel bounds | ✓ PASS |
| **TOUCHING** | Candidate boundary touches adjacent parcel edge within 0.05m tolerance | ✓ PASS |
| **OVERLAPPING** | Candidate polygon intersects adjacent parcel > 0.05m² | ⚠ SPATIAL COLLISION (`REVIEW_REQUIRED`) |
| **DISJOINT** | Candidate polygon is located away from target parcel | ⚠ MISMATCH (`REVIEW_REQUIRED`) |

---

## 4. Multi-Factor Spatial Risk Engine
Computes a risk score (0 to 100):
- **0 - 25 (LOW RISK):** High coordinate confidence, exact cadastral match, 0.0 sq.m overlap.
- **26 - 50 (MEDIUM RISK):** Slight area variance (5-10%), centroid reconstruction.
- **51 - 100 (HIGH RISK):** Boundary collision detected, significant area mismatch (>15%), or invalid self-intersecting geometry.
