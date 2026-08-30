# PlotProof OCR & Document Intelligence

## 1. Pipeline Overview
The OCR subsystem extracts statutory metadata from unstructured deed scans without determining legal ownership.

```
PDF / Image Scanned Deed
         │
         ▼
   PyMuPDF Page Splitter (300 DPI)
         │
         ▼
 OpenCV Preprocessing Pipeline
   ├── Grayscale Conversion
   ├── Otsu Adaptive Thresholding
   ├── Morphological Denoising
   └── Hough Line Transform Deskew
         │
         ▼
 Dual OCR Engine Dispatch
   ├── Tesseract OCR (Tamil / Bilingual Script)
   └── EasyOCR (English / Alphanumeric Deeds)
         │
         ▼
 Regex & Entity Extraction Engine
   ├── Survey & Subdivision Numbers (e.g. 142/3A, புல எண் 142/3A)
   ├── District, Taluk, Village
   ├── Extent & Area Units (Sq.ft, Acres, Cents, Gunthas, Grounds)
   ├── Four-Point Boundary Descriptions (North, South, East, West)
   └── GPS Coordinates (Latitude, Longitude)
         │
         ▼
 Normalization & Validation Handshake
```

---

## 2. Unit Conversions to Standard Square Meters (m²)

| Input Unit | Conversion Factor to m² | Example |
|:---|:---|:---|
| **Acre / Acres** | 4046.8564 m² | `1 Acre` &rarr; `4046.86 m²` |
| **Cent / Cents** | 40.4686 m² | `5.5 Cents` &rarr; `222.58 m²` |
| **Ground / Grounds** | 222.96 m² | `1 Ground` &rarr; `222.96 m²` |
| **Guntha / Gunthas** | 101.17 m² | `2 Gunthas` &rarr; `202.34 m²` |
| **Hectare / Hectares** | 10,000.00 m² | `1 Hectare` &rarr; `10000.00 m²` |
| **Sq.ft / Square Feet**| 0.092903 m² | `2400 Sq.ft` &rarr; `222.96 m²` |

---

## 3. Human Review Flagging
Missing mandatory fields (e.g., missing survey number, unparseable coordinates, confidence < 75%) automatically flag the processing job as `REVIEW_REQUIRED` for Sub-Registrar confirmation.
