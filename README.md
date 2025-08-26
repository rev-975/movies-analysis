# Movies Analysis App

A **PyQt5 desktop application** for analyzing movie datasets with interactive plots and a searchable DataFrame.  

This app allows you to visualize various aspects of movies, such as revenue, genres, directors, budgets, and runtime distributions.  

---

## Features

- View the full DataFrame with sortable columns and search filters.  
- Horizontal bar plots for:
  - Highest grossing movies  
  - Top production companies by revenue  
  - Directors by score and gross  
  - Revenue and score by country  
- Distribution plots for budget and runtime.  
- Visualizations for preferred genres and rating popularity.  
- Interactive buttons for easy navigation between views.

---

## Requirements

- Python 3.8+  
- PyQt5  
- pandas  
- matplotlib  
- numpy  

## Setup Instructions

1. Clone or download this repository.
2. Ensure Python 3.8+ is installed.
3. Install required packages using pip:

```bash
pip install PyQt5 pandas matplotlib numpy
```

or using pacman or yay on Arch distributions 

```bash
sudo pacman -S python python-pyqt5 python-pandas python-matplotlib python-numpy
```

4. Run the file movies.py

---

## Dataset

The application uses a CSV file named `movies.csv` with at least the following columns:

```
name, year, genre, company, director, country, gross, budget, runtime, score, rating
```

Optional columns like `votes`, `released`, `writer`, `star` will be ignored.  

**Dataset location:**  

Save the CSV at:

```
~/movies_analysis/movies.csv
```

or update the path in the code:

```python
data = pd.read_csv('~/movies_analysis/movies.csv')
```

You can use your own movie dataset as long as it contains the required columns.

---

## Usage

- Launch the app to see the **DataFrame view** by default.  
- Use the **search boxes** above each column to filter results.  
- Click **buttons** to switch between visualizations:  
  - Horizontal bar plots for revenue, directors, genres, and countries.  
  - Distribution plots for budget and runtime.  
  - Plots for preferred genres and rating popularity.  

---

## Notes

- only the top N items are plotted for plots like “Top Directors” or “Revenue by Country” (otherwise it takes a bit of time)  

