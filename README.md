# Movies Analysis Dashboard (PyQt5 + Matplotlib)

This project is an interactive data analysis dashboard for movies, built with PyQt5 for the GUI, Matplotlib for visualizations, and Pandas for data handling. It allows users to explore a movies dataset through tables, filtering, sorting, and various plots (e.g., revenue trends, genre popularity, director performance).

## Features

- Data Table with Filtering & Sorting
  - View the dataset in a table.
  - Sort by any column.

- Interactive Visualizations
  - Highest grossing movies
  - Top production companies by revenue
  - Genre popularity
  - Gross revenue by genre
  - Revenue by country
  - Scores by country
  - Directors by score and revenue
  - Budget distribution
  - Runtime distribution
  - Budget vs revenue trends over years
  - Rating distribution

- Custom Styling

## Tech Stack

- Python 3
- PyQt5 – GUI framework
- Matplotlib – Data visualization
- Pandas – Data manipulation
- NumPy – Numerical operations

## Dataset

The app expects a CSV file containing movies data at:  
```
~/movies_analysis/movies.csv
```

The dataset should include at least the following columns:
- `name` – Movie name  
- `company` – Production company  
- `genre` – Movie genre  
- `country` – Country of release  
- `director` – Movie director  
- `budget` – Budget in USD  
- `gross` – Gross revenue in USD  
- `runtime` – Runtime in minutes  
- `score` – Rating score  
- `rating` – Audience rating (e.g., PG-13, R)  
- `year` – Release year  

Unused or unnecessary columns (`votes`, `released`, `writer`, `star`) are dropped automatically.

## How to Run

1. Clone or download this repository.  

2. Install dependencies:
   ```bash
   pip install pandas matplotlib pyqt5
   ```

3. Place your `movies.csv` file in:
   ```
   ~/movies_analysis/movies.csv
   ```
   You can use your own movie dataset as long as it contains the required columns.
   just change the filename in the python file.

4. Run the application:
   ```bash
   python3 movies_final.py
   ```

## Future Improvements

- Export filtered data to CSV/Excel.  
- Add more interactive plots (scatter plots, correlation heatmaps).  
- Improve performance with large datasets.  
- Switch to PySide6 for Qt6 compatibility.  

## License

This project is open-source. Use and modify freely for personal or academic purposes.  
