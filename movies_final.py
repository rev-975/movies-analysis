import sys
import pandas as pd # library for data manipulation and analysis, which allows for easy handling of data
import matplotlib.pyplot as plt # plotting library that is used to create static, animated, and interactive visualizations
import numpy as np 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableView, QHBoxLayout, QLineEdit, QFrame, QLabel, QHeaderView, QScrollArea, QShortcut
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QKeySequence
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
    def __init__(self, df=pd.DataFrame()):
        super().__init__()
        self._original_data = df.copy()
        self._filtered_data = df.copy()
        self._filters = {}

    def rowCount(self, parent=QModelIndex()):
        return len(self._filtered_data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._filtered_data.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._filtered_data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                column_name = self._filtered_data.columns[section]
                filter_text = self._filters.get(column_name, "")
                indicator = " 🔍" if filter_text else ""
                return f"{column_name}{indicator}"
            else:
                return str(self._filtered_data.index[section])
        return None

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        column_name = self._filtered_data.columns[column]
        self._filtered_data = self._filtered_data.sort_values(by=column_name, ascending=(order == Qt.AscendingOrder))
        self.layoutChanged.emit()
    
    def apply_filter(self, column_name, filter_text):
        print(f"Applying filter to column '{column_name}' with text '{filter_text}'")  
        
        if filter_text.strip():
            self._filters[column_name] = filter_text.strip()
        else:
            self._filters.pop(column_name, None)
        
        self.layoutAboutToBeChanged.emit()
        
        filtered_data = self._original_data.copy()
        
        print(f"Active filters: {self._filters}")  # debug print
        
        for column_name, filter_text in self._filters.items():
             print(f"Filtering column '{column_name}' with '{filter_text}'")  
               
             column_data = filtered_data[column_name]
               
             if pd.api.types.is_numeric_dtype(column_data):
                 try:
                     numeric_value = float(filter_text)
                     mask = column_data == numeric_value
                 except ValueError:
                     mask = column_data.astype(str).str.contains(
                         filter_text, case=False, na=False, regex=False
                     )
             else:
                 mask = column_data.astype(str).str.contains(
                     filter_text, case=False, na=False, regex=False
                 )
               
             filtered_data = filtered_data[mask]
             print(f"After filtering '{column_name}': {len(filtered_data)} rows remaining")  
        
        self._filtered_data = filtered_data
        self.layoutChanged.emit()

    def clear_all_filters(self):
        self._filters.clear()
        self._filtered_data = self._original_data.copy()
        self.layoutAboutToBeChanged.emit()
        self.layoutChanged.emit()

    def get_active_filters(self):
        return self._filters.copy()


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movies Analysis")

        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setSpacing(8)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.sidebar)
        scroll_area.setFixedWidth(250)

        shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut.activated.connect(lambda: self.search_input.setFocus())

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
        self.content_layout.setContentsMargins(10, 10, 10, 10)

        # creating a placeholder for DataFrame and plotting
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.content_layout.addWidget(self.table_view, 1)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.content_layout.addWidget(self.canvas, 1)
        
        self.canvas.setVisible(False) #first hide canvas show only df

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
            self.ax.text(val+0.03, bar.get_y() + bar.get_height()/2, label, va='center', color='black')
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

    def setup_column_filters(self):
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(5)
        filter_layout.setContentsMargins(5, 5, 5, 5)
        
        self.column_filters = {}
        
        for column in data.columns:
            col_container = QWidget()
            col_layout = QVBoxLayout(col_container)
            col_layout.setContentsMargins(2, 2, 2, 2)
            col_layout.setSpacing(2)
            
            col_label = QLabel(column)
            col_label.setAlignment(Qt.AlignCenter)
            col_label.setStyleSheet("font-weight: bold; font-size: 10px;")
            col_layout.addWidget(col_label)
            
            filter_input = QLineEdit()
            filter_input.setPlaceholderText(f"Filter")
            filter_input.setMaximumWidth(120)
            filter_input.setToolTip(f"Search in {column} column")
            
            def make_filter_handler(col_name):
                return lambda text: self.apply_column_filter(col_name, text)
            
            filter_input.textChanged.connect(make_filter_handler(column))
            
            col_layout.addWidget(filter_input)
            self.column_filters[column] = filter_input
            
            filter_layout.addWidget(col_container)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.setIcon(qta.icon("fa5s.eraser", color="white"))
        clear_btn.clicked.connect(self.clear_all_filters)
        clear_btn.setMaximumWidth(80)
        filter_layout.addWidget(clear_btn)
        
        filter_layout.addStretch()
        
        self.content_layout.insertWidget(0, filter_frame)

    def apply_column_filter(self, column_name, filter_text):
        if hasattr(self, 'model') and self.model:
            self.model.apply_filter(column_name, filter_text)
    
    def clear_all_filters(self):
        for filter_input in self.column_filters.values():
            filter_input.clear()
        
        if hasattr(self, 'model') and self.model:
            self.model.clear_all_filters()

    def show_dataframe_only(self):
        self.table_view.setVisible(True)
        self.canvas.setVisible(False)
    
    def show_plot_only(self):
        self.table_view.setVisible(False)
        self.canvas.setVisible(True)

    def view_dataframe(self):
        # clear previous plot
        self.ax.clear()
        self.canvas.draw()

        self.model = PandasModel(data)
        self.table_view.setModel(self.model)

        header = self.table_view.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.sortIndicatorChanged.connect(self.handle_column_click)

        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        if not hasattr(self, 'column_filters'):
            self.setup_column_filters()

        self.show_dataframe_only()

        self.table_view.update()
        self.table_view.viewport().update()
        self.table_view.horizontalHeader().update()

    def handle_column_click(self, index, order):
        self.model.sort(index, order)

    def missing_columns(self):
        self.ax.text(0.5, 0.5, 'Missing required columns',
                     ha='center', va='center', color='black')
        self.canvas.draw()

    def name_vs_gross(self):
        self.ax.clear()
        if 'gross' in data.columns:
            top_movies = data.sort_values(by='gross', ascending=False).head(15)
            self.draw_barh(top_movies.set_index('name')['gross'],
                           'Top 15 Highest Grossing Movies', 'Gross Revenue (Billions)', 'Movie Name', True)
        else:
            self.missing_columns()
        self.show_plot_only() 
        self.canvas.draw()

    def company_vs_revenue(self):
        self.ax.clear()
        if 'company' in data.columns and 'gross' in data.columns:
            top_companies = data.groupby('company')['gross'].mean().nlargest(10)
            self.draw_barh(top_companies, 'Top 10 Production Companies by Revenue',
                           'Revenue (Billions)', 'Company', True)
        else:
            self.missing_columns()
        self.show_plot_only() 
        self.canvas.draw()

    def genre_vs_freq(self):
        self.ax.clear()
        if 'genre' in data.columns:
            counts = data['genre'].value_counts()
            self.draw_bar(counts, 'Genres Popularity', 'Genre', 'Count')
        else:
            self.missing_columns()
        self.show_plot_only() 
        self.canvas.draw()

    def genre_vs_gross(self):
        self.ax.clear()
        if 'genre' in data.columns and 'gross' in data.columns:
            medians = data.groupby('genre')['gross'].median().sort_values(ascending=False)
            self.draw_bar(medians, 'Median Gross by Genre', 'Genre', 'Gross (Billions)', True)
        else:
            self.missing_columns()
        self.show_plot_only() 
        self.canvas.draw()

    def country_vs_revenue(self):
        self.ax.clear()
        if 'country' in data.columns and 'gross' in data.columns:
            medians = data.groupby('country')['gross'].median().nlargest(10)
            self.draw_bar(medians, 'Median Gross Revenue by Country (Top 10)', 'Country', 'Revenue (Billions)', True)
        else:
            self.missing_columns()
        self.show_plot_only() 
        self.canvas.draw()

    def country_vs_score(self):
        self.ax.clear()
        if 'country' in data.columns and 'score' in data.columns:
            avg = data.groupby('country')['score'].mean().nlargest(20)
            self.draw_barh(avg, 'Average Ratings by Country', 'Score', 'Country')
        else:
            self.missing_columns()
        self.show_plot_only() 
        self.canvas.draw()

    def directors_score(self):
        self.ax.clear()
        if 'director' in data.columns and 'score' in data.columns:
            avg = data.groupby('director')['score'].mean().nlargest(25)
            self.draw_barh(avg, 'Directors by Average Score', 'Score', 'Director')
        else:
            self.missing_columns()
        self.show_plot_only() 
        self.canvas.draw()

    def directors_gross(self):
        self.ax.clear()
        if 'director' in data.columns and 'gross' in data.columns:
            totals = data.groupby('director')['gross'].sum().nlargest(25)
            self.draw_barh(totals, 'Directors by Gross Revenue', 'Gross (Billions)', 'Director', True)
        else:
            self.missing_columns()
        self.show_plot_only() 
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
        self.show_plot_only() 
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
        self.show_plot_only() 
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
        self.show_plot_only() 
        self.canvas.draw()

    def preferred_genres(self):
        self.ax.clear()
        if 'genre' in data.columns:
            counts = data['genre'].value_counts().nlargest(15)
            self.draw_bar(counts, 'Preferred Genres', 'Genre', 'Count')
        else:
            self.missing_columns()
        self.show_plot_only() 
        self.canvas.draw()

    def rating_popularity(self):
        self.ax.clear()
        if 'rating' in data.columns:
            counts = data['rating'].value_counts()
            self.draw_bar(counts, 'Rating Distribution', 'Rating', 'Count')
        else:
            self.missing_columns()
        self.show_plot_only() 
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet()) 
    window = App()
    window.show()
    sys.exit(app.exec_())
