import sys
import pandas as pd # library for data manipulation and analysis, which allows for easy handling of data
import matplotlib.pyplot as plt # plotting library that is used to create static, animated, and interactive visualizations
import numpy as np 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableView, QHBoxLayout, QLineEdit, QLabel, QHeaderView, QScrollArea
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
import random # used to randomly select colors for the plots
import textwrap # used to format long strings of text (like movie titles) into multiple lines for better readability.
import qtawesome as qta
import qdarkstyle  

# loading and cleaning up data
data = pd.read_csv('~/movies_analysis/movies.csv')
data.drop_duplicates(inplace=True)
data.dropna(inplace=True)  # removes rows with missing values
data.drop(['votes', 'released', 'writer', 'star'], axis=1, inplace=True) # removing unused attributes

#data.rename(columns = {'budget':'budget ($)', 'gross': 'gross ($)'}, inplace = True)
plt.style.use("seaborn-v0_8-darkgrid")
ACCENT_COLOR = "#FF5252"

#model for displaying df
class PandasModel(QAbstractTableModel):
    def __init__(self, data_frame=pd.DataFrame()):
        super().__init__()
        self._original_data = data_frame
        self._data = data_frame

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            else:
                return str(self._data.index[section])
        return None

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        column_name = self._data.columns[column]
        self._data = self._data.sort_values(by=column_name, ascending=(order == Qt.AscendingOrder))
        self.layoutChanged.emit()

    def filter(self, column, query):
        self.layoutAboutToBeChanged.emit()
        if query:
            mask = self._original_data.iloc[:, column].astype(str).str.contains(query, case=False, na=False)
            self._data = self._original_data[mask]
        else:
            self._data = self._original_data
        self.layoutChanged.emit()

# Main Application
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 Movies Analysis")
        self.resize(1500, 900)

        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setSpacing(8)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.sidebar)
        scroll_area.setFixedWidth(250)

        # maps button labels to their corresponding methods
        button_actions = {
            "View DataFrame": (self.view_dataframe, "fa5s.table"),
            "Name vs Gross Revenue": (self.name_vs_gross, "fa5s.chart-bar"),
            "Companies vs Revenue": (self.company_vs_revenue, "fa5s.building"),
            "Genre vs Freq": (self.genre_vs_freq, "fa5s.film"),
            "Budget and Revenue": (self.budget_revenue, "fa5s.chart-line"),
            "Genres vs Gross": (self.genre_vs_gross, "fa5s.chart-pie"),
            "Revenue by Country": (self.country_vs_revenue, "fa5s.globe"),
            "Score by Country": (self.country_vs_score, "fa5s.star"),
            "Directors Score": (self.directors_score, "fa5s.user"),
            "Directors vs Gross": (self.directors_gross, "fa5s.user-tie"),
            "Budget Distribution": (self.budget_distribution, "fa5s.money-bill-wave"),
            "Runtime Distribution": (self.runtime_distribution, "fa5s.clock"),
            "Preferred Genres": (self.preferred_genres, "fa5s.list"),
            "Rating Popularity": (self.rating_popularity, "fa5s.thumbs-up"),
        }

        for text, (action, icon_name) in button_actions.items():
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon_name, color="white"))
            btn.clicked.connect(action)
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch()

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(16)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        # creating a placeholder for DataFrame and plotting
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.content_layout.addWidget(self.table_view, 2)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.content_layout.addWidget(self.canvas, 3)

        container = QWidget()
        main_layout = QHBoxLayout(container)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.content_widget)
        self.setCentralWidget(container)

        self.model = None
        self.view_dataframe()

    def draw_barh(self, series, title, xlabel, ylabel, is_currency=False):
        bars = self.ax.barh(series.index, series.values, color=ACCENT_COLOR)
        for bar in bars:
            val = bar.get_width()
            label = f"${val/1e9:.1f}B" if is_currency else f"{val:.2f}"
            self.ax.text(val, bar.get_y() + bar.get_height()/2, label, va='center', color='black')
        self.ax.set_title(title, color='black', fontsize=14, weight='bold')
        self.ax.set_xlabel(xlabel, color='black')
        self.ax.set_ylabel(ylabel, color='black')
        self.figure.tight_layout()

    def draw_bar(self, series, title, xlabel, ylabel, is_currency=False):
        bars = self.ax.bar(series.index, series.values, color=ACCENT_COLOR)
        for bar in bars:
            val = bar.get_height()
            label = f"${val/1e9:.1f}B" if is_currency else str(int(val))
            self.ax.text(bar.get_x() + bar.get_width()/2, val, label, ha='center', va='bottom', color='black')
        self.ax.set_title(title, color='black', fontsize=14, weight='bold')
        self.ax.set_xlabel(xlabel, color='black')
        self.ax.set_ylabel(ylabel, color='black')
        self.figure.tight_layout()

    def view_dataframe(self):

        # clear previous plot
        self.ax.clear()
        self.canvas.draw()

        self.model = PandasModel(data)
        self.table_view.setModel(self.model)

        header = self.table_view.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.sortIndicatorChanged.connect(self.handle_column_click)
        header.setSectionResizeMode(QHeaderView.Stretch)

        # update the header
        self.table_view.update()
        self.table_view.viewport().update()
        self.table_view.horizontalHeader().update()

    def handle_column_click(self, index, order):
        self.model.sort(index, order)

    def missing_columns(self):
        self.ax.text(0.5, 0.5, 'Missing required columns',
                     ha='center', va='center', color='black')
        self.canvas.draw()

    # --- Plots ---
    def name_vs_gross(self):
        self.ax.clear()
        if 'gross' in data.columns:
            top_movies = data.sort_values(by='gross', ascending=False).head(15)
            self.draw_barh(top_movies.set_index('name')['gross'],
                           'Top 15 Highest Grossing Movies', 'Gross Revenue (Billions)', 'Movie Name', True)
        else:
            self.missing_columns()
        self.canvas.draw()

    def company_vs_revenue(self):
        self.ax.clear()
        if 'company' in data.columns and 'gross' in data.columns:
            top_companies = data.groupby('company')['gross'].mean().nlargest(10)
            self.draw_barh(top_companies, 'Top 10 Production Companies by Revenue',
                           'Revenue (Billions)', 'Company', True)
        else:
            self.missing_columns()
        self.canvas.draw()

    def genre_vs_freq(self):
        self.ax.clear()
        if 'genre' in data.columns:
            counts = data['genre'].value_counts()
            self.draw_bar(counts, 'Genres Popularity', 'Genre', 'Count')
        else:
            self.missing_columns()
        self.canvas.draw()

    def genre_vs_gross(self):
        self.ax.clear()
        if 'genre' in data.columns and 'gross' in data.columns:
            medians = data.groupby('genre')['gross'].median().sort_values(ascending=False)
            self.draw_bar(medians, 'Median Gross by Genre', 'Genre', 'Gross (Billions)', True)
        else:
            self.missing_columns()
        self.canvas.draw()

    def country_vs_revenue(self):
        self.ax.clear()
        if 'country' in data.columns and 'gross' in data.columns:
            medians = data.groupby('country')['gross'].median().nlargest(10)
            self.draw_bar(medians, 'Median Gross Revenue by Country (Top 10)', 'Country', 'Revenue (Billions)', True)
        else:
            self.missing_columns()
        self.canvas.draw()

    def country_vs_score(self):
        self.ax.clear()
        if 'country' in data.columns and 'score' in data.columns:
            avg = data.groupby('country')['score'].mean().nlargest(20)
            self.draw_barh(avg, 'Average Ratings by Country', 'Score', 'Country')
        else:
            self.missing_columns()
        self.canvas.draw()

    def directors_score(self):
        self.ax.clear()
        if 'director' in data.columns and 'score' in data.columns:
            avg = data.groupby('director')['score'].mean().nlargest(25)
            self.draw_barh(avg, 'Directors by Average Score', 'Score', 'Director')
        else:
            self.missing_columns()
        self.canvas.draw()

    def directors_gross(self):
        self.ax.clear()
        if 'director' in data.columns and 'gross' in data.columns:
            totals = data.groupby('director')['gross'].sum().nlargest(25)
            self.draw_barh(totals, 'Directors by Gross Revenue', 'Gross (Billions)', 'Director', True)
        else:
            self.missing_columns()
        self.canvas.draw()

    def budget_distribution(self):
        self.ax.clear()
        if 'budget' in data.columns:
            self.ax.hist(data['budget'], bins=30, color=ACCENT_COLOR, edgecolor='black')
            self.ax.set_title('Budget Distribution', fontsize=14, weight='bold')
            self.ax.set_xlabel('Budget', color='black')
            self.ax.set_ylabel('Frequency', color='black')
        else:
            self.missing_columns()
        self.canvas.draw()

    def runtime_distribution(self):
        self.ax.clear()
        if 'runtime' in data.columns:
            self.ax.hist(data['runtime'], bins=30, color=ACCENT_COLOR, edgecolor='black')
            self.ax.set_title('Runtime Distribution', color='black', fontsize=14, weight='bold')
            self.ax.set_xlabel('Runtime (minutes)', color='black')
            self.ax.set_ylabel('Frequency', color='black')
        else:
            self.missing_columns()
        self.canvas.draw()

    def budget_revenue(self):
        self.ax.clear()
        if 'budget' in data.columns and 'gross' in data.columns:
            df = data.groupby('year').agg({'budget': 'mean', 'gross': 'mean'})
            self.ax.plot(df.index, df['budget'], label='Budget', color=ACCENT_COLOR)
            self.ax.plot(df.index, df['gross'], label='Gross', color='black')
            self.ax.set_title('Budget vs Revenue Over Years', color='black', fontsize=14, weight='bold')
            self.ax.set_xlabel('Year', color='black')
            self.ax.set_ylabel('Amount', color='black')
            self.ax.legend()
        else:
            self.missing_columns()
        self.canvas.draw()

    def preferred_genres(self):
        self.ax.clear()
        if 'genre' in data.columns:
            counts = data['genre'].value_counts().nlargest(15)
            self.draw_bar(counts, 'Preferred Genres', 'Genre', 'Count')
        else:
            self.missing_columns()
        self.canvas.draw()

    def rating_popularity(self):
        self.ax.clear()
        if 'rating' in data.columns:
            counts = data['rating'].value_counts()
            self.draw_bar(counts, 'Rating Distribution', 'Rating', 'Count')
        else:
            self.missing_columns()
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet()) 
    window = App()
    window.show()
    sys.exit(app.exec_())
