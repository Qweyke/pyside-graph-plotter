# pyside-symbolic-plotter

## Project Goal
The goal of this project is to provide a high-performance mathematical visualization tool capable of handling complex symbolic expressions and numerical discontinuities with high precision. 

Unlike standard "black-box" browser plotters, this tool focuses on local data integrity, custom rendering styles, and a robust "lift-the-pen" logic. It ensures that functions with asymptotes, such as $1/x$ or $10/\sin(x)$, are rendered without the misleading vertical lines common in simpler plotting software.



## Key Technical Challenges Solved
* **Symbolic-to-Numerical Pipeline**: Utilizes `SymPy` for expression parsing and `NumPy` for vectorized, high-performance data generation.
* **Intelligent Discontinuity Handling**: Implemented a custom rendering loop that detects `NaN` and infinite values to prevent visual artifacts at mathematical gaps.
* **Advanced Coordinate Mapping**: Features a standalone `CoordinateMapper` that translates an infinite mathematical plane into a finite pixel grid, supporting dynamic axis signatures on the outer contour.
* **Multi-Function Metadata Management**: Leverages `QListWidgetItem` data roles to cache pre-calculated math arrays and visual styles (color, pen style), allowing for instantaneous UI updates.



## Project Structure
This project utilizes the industry-standard `src` layout to separate the application logic from project metadata and tests.

```text
pyside-symbolic-plotter/
├── src/
│   └── plotter/
│       ├── core/           # Math engines & coordinate mapping
│       │   ├── resolver.py # Symbolic solving logic
│       │   └── mapper.py   # Coordinate transformation
│       ├── gui/            # PySide6 interface components
│       │   ├── main_window.py
│       │   └── canvas.py   # Custom plotting widget
│       ├── rendering/      # The drawing engine
│       │   └── builder.py  # QPainterPath & pen logic
│       └── main.py         # Application entry point
├── tests/                  # Unit tests for math verification
├── README.md               # Project documentation
└── pyproject.toml          # Build system configuration

