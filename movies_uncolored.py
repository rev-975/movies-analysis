import textwrap
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableView, QHBoxLayout, QLineEdit, QLabel, QHeaderView, QSizePolicy, QSplitter
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QFont
import random

data = pd.read_csv('~/movies_analysis/movies.csv')
data.drop_duplicates(inplace=True)
data.dropna(inplace=True)

data.drop(['votes', 'released', 'writer'], axis=1, inplace=True)
#list of colors
colors = ['lightcoral', 'indianred','maroon', 'red', 'saddlebrown', 'peru', 'darkorange', 'tan','gold','plum','tomato','forestgreen','darkgreen','green','lime','seagreen','mediumspringgreen','mediumaquamarine','turquoise', 'darkslategrey','teal','dodgerblue','deepskyblue','cornflowerblue','navy','indigo','blue','mediumslateblue','darkviolet','fuchsia','deeppink','magenta','crimson']

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

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            else:
                return str(self._data.index[section])
        return None

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        column_name = self._data.columns[column]
        self._data = self._data.sort_values(by=column_name, ascending=(order == Qt.SortOrder.AscendingOrder))
        self.layoutChanged.emit()

    def filter(self, column, query):
        self.layoutAboutToBeChanged.emit()
        if query:
            mask = self._original_data.iloc[:, column].astype(str).str.contains(query, case=False, na=False)
            self._data = self._original_data[mask]
        else:
            self._data = self._original_data
        self.layoutChanged.emit()

# main application
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movies Analysis")
#        self.setFont(QFont("DejaVu Sans Mono", 10))
        #self.setGeometry(150, 150, 1200, 800)

# creating a central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # creating a horizontal layout for buttons
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        # defining button actions
        button_actions = {
            "View DataFrame": self.view_dataframe,
            "Name vs Gross Revenue": self.name_vs_gross,
#            "Rating Plot": lambda: self.show_plot('rating'),
            "Companies vs Revenue": self.company_vs_revenue,
            "Genre vs Freq": self.genre_vs_freq,
            "Budget and Revenue": self.budget_revenue,
            "Genres vs Gross": self.genre_vs_gross,
            "Revenue by Country": self.country_vs_revenue,
            "Score by Country": self.country_vs_score,
            "Directors Score": self.directors_score,
            "Directors vs Gross": self.directors_gross,
            "Budget Distribution": self.budget_distribution,
            "Runtime Distribution": self.runtime_distribution,
            "Preferred Genres": self.preferred_genres,
            "Rating Popularity": self.rating_popularity,
        }
                # creating buttons and adding to layout
        for text, action in button_actions.items():
            wrap_text = textwrap.fill(text, width=20)  # Adjust width as needed
            button = QPushButton(wrap_text)
            button.clicked.connect(action)
            self.button_layout.addWidget(button)

        self.splitter = QSplitter(Qt.Vertical)
        self.layout.addWidget(self.splitter)
        self.data_frame_widget = QWidget()
        self.data_frame_layout = QVBoxLayout(self.data_frame_widget)

        # creating a placeholder for DataFrame and plotting
        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)
        self.table_view.setMaximumHeight(500)  # can set maximum height to make it smaller- hopefully

        # creating search boxes for each column
        self.search_layout = QHBoxLayout()
        self.layout.addLayout(self.search_layout)
        self.splitter.addWidget(self.data_frame_widget)
        self.plot_widget = QWidget()
        self.plot_layout = QVBoxLayout(self.plot_widget)
        self.search_boxes = []
        self.model = None

        # create a matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.central_widget.setLayout(self.layout)
        self.button_layout.setSpacing(10)
        self.button_layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.plot_layout.addWidget(self.canvas)
        self.splitter.addWidget(self.plot_widget)
        # initially show the DataFrame
        self.view_dataframe()

    def view_dataframe(self):
        # clear previous plot- leads to unknown bugs otherwise
        self.ax.clear()
        self.canvas.draw()

        # show DataFrame
        self.model = PandasModel(data)
        self.table_view.setModel(self.model)

        # sorting
        header = self.table_view.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.sortIndicatorChanged.connect(self.handle_column_click)

        # clear previous search boxes
        self.clear_search_boxes()

        # adding search boxes
        for i in range(self.model.columnCount()):
            search_box = QLineEdit()
            search_box.setPlaceholderText(f"Search {self.model.headerData(i, Qt.Horizontal, Qt.ItemDataRole.DisplayRole)}")
            search_box.textChanged.connect(lambda text, col=i: self.handle_search(text, col))
            self.search_boxes.append(search_box)
            self.search_layout.addWidget(QLabel(self.model.headerData(i, Qt.Horizontal, Qt.ItemDataRole.DisplayRole)))
            self.search_layout.addWidget(search_box)

        header.setSectionResizeMode(QHeaderView.Stretch)  # stretch columns to fit the table width
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        header.setSectionResizeMode(QHeaderView.Stretch)

# update the header
        self.table_view.update()
        self.table_view.viewport().update()
        self.table_view.horizontalHeader().update()

    def clear_search_boxes(self):
        # remove existing search boxes and labels
        for box in self.search_boxes:
            box.deleteLater()
        self.search_boxes.clear()

        # clear layout items
        while self.search_layout.count():
            item = self.search_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def handle_column_click(self, index, order):
        # sort model based on the clicked column
        self.model.sort(index, order)

    def handle_search(self, text, column):
        # apply filter based on the search box
        self.model.filter(column, text)

    def missing_columns(self):
        self.ax.text(0.5, 0.5, 'Missing required columns. Sorry.', horizontalalignment='center', verticalalignment='center', color='black')

    def name_vs_gross(self):
        self.ax.clear()
        if 'gross' in data.columns:
            highest_grossing_movies = data.sort_values(by='gross', ascending=False).head(10)
            names = highest_grossing_movies['name']
            wrap_names = [textwrap.fill(name, width=20) for name in names]  # Adjust width as needed
            gross = highest_grossing_movies['gross']
            bars = self.ax.barh(wrap_names, gross, color=random.choice(colors))
            for bar in bars:
                width = bar.get_width()
                self.ax.text(width + 1e7, bar.get_y() + bar.get_height()/2, f'${width/1e9:.1f}B', va='center', color='black')
            
            self.ax.set_title('10 Highest Grossing Movies', color='black')
            self.ax.set_xlabel('Gross Revenue (Billions)', color='black')
            self.ax.set_ylabel('Movie Name', color='black')
        else:
            self.missing_columns()
        self.canvas.draw()

    def company_vs_revenue(self):
        self.ax.clear()
        if 'company' in data.columns and 'gross' in data.columns:
            # get the top 10 production companies based on mean gross revenue
            top_10_companies = data.groupby('company')['gross'].mean().nlargest(10).index
            # filtering the data to include only the top 15 companies
            data_top_10 = data[data['company'].isin(top_10_companies)]
            # sort the data by mean gross revenue in descending order
            data_top_10_sorted = data_top_10.groupby('company')['gross'].mean().reset_index().sort_values(by='gross', ascending=False)
    
            company = data_top_10_sorted['company']
            gross = data_top_10_sorted['gross']
            wrap_company = [textwrap.fill(name, width=20) for name in company]  # Adjust width as needed
            bars = self.ax.barh(wrap_company, gross, color=random.choice(colors))
            for bar in bars:
                 width = bar.get_width()
                 self.ax.text(width + 1e7, bar.get_y() + bar.get_height()/2, f'${width/1e9:.1f}B', va='center', color='black')
    
            self.ax.set_title('Top 10 Production Companies by Revenue', color='black')
            self.ax.set_ylabel('Production Company', color='black')
            self.ax.set_xlabel('Total Revenue(in Billions)', color='black')
        else:
            self.missing_columns()
        self.canvas.draw()

    def genre_vs_freq(self):
        self.ax.clear()
        if 'genre' in data.columns:
            genre_counts = data['genre'].value_counts().sort_values(ascending=False)
            self.ax.bar(genre_counts.index, genre_counts.values, color=random.choice(colors))
            self.ax.set_title('Genres Popularity', color='black')
            self.ax.set_xlabel('Genre', color='black')
            self.ax.set_ylabel('Count', color='black')
        else:
            self.missing_columns()
        self.canvas.draw()

    def genre_vs_gross(self):
        self.ax.clear()
        if 'genre' in data.columns and 'gross' in data.columns:
        # we use median bc data might be skewed
            median_gross_by_genre = data.groupby('genre')['gross'].median().sort_values(ascending=False)
            self.ax.bar(median_gross_by_genre.index, median_gross_by_genre.values, color=random.choice(colors))
            self.ax.set_title('Mean Gross by Genre')
            self.ax.set_xlabel('Genre')
            self.ax.set_ylabel('Gross')
        else:
            self.missing_columns()
        self.canvas.draw()

    def country_vs_revenue(self):
        self.ax.clear()
        if 'country' in data.columns and 'gross' in data.columns:
            # similar to top companies vs revenueindex
            # we use median because data wrt country might be skewed
            top_10_countries = data.groupby('country')['gross'].median().nlargest(10).index
            data_top_10_countries = data[data['country'].isin(top_10_countries)].sort_values(ascending=False, by='gross')
            self.ax.bar(data_top_10_countries.country, data_top_10_countries.gross, color=random.choice(colors))
            self.ax.set_title('Median Gross Revenue by Country (Top 10 Countries)')
            self.ax.set_xlabel('Country', color = 'black')
            self.ax.set_ylabel('Median Gross Revenue', color = 'black')
        else:
             self.missing_columns()
        self.canvas.draw()


    def country_vs_score(self):
        self.ax.clear()
        if 'country' in data.columns and 'score' in data.columns:
            avg_rating_by_country = data.groupby('country')['score'].mean().sort_values(ascending=False).head(20)
            self.ax.barh(avg_rating_by_country.index, avg_rating_by_country.values,  color=random.choice(colors))
            for index, value in enumerate(avg_rating_by_country.values):
                self.ax.text(value + 0.01, index, f'{value:.2f}', va='center')
            self.ax.set_title('Avg Ratings by Country', color = 'black')
            self.ax.set_xlabel('Country', color = 'black')
            self.ax.set_ylabel('Ratings', color = 'black')
            
        else:
            self.missing_columns()
        self.canvas.draw()


    def directors_score(self):
        # directors by score
        self.ax.clear()
        if 'director' in data.columns and 'score' in data.columns:
            directors = data.groupby('director')['score'].mean().nlargest(25)
            bars = self.ax.barh(directors.index, directors.values,  color=random.choice(colors))
            for bar in bars:
                height = bar.get_height()
                width = bar.get_width()
                self.ax.text(width + 0.01, bar.get_y() + bar.get_height()/2, f'{width:.2f}', va='center', color='black')
            self.ax.set_title('Directors by Score', color='black')
            self.ax.set_xlabel('Director', color='black')
            self.ax.set_ylabel('Average Score', color='black')
        else:
            self.missing_columns()
        self.canvas.draw()

    def directors_gross(self):
        # directors vs gross
        self.ax.clear()
        if 'director' in data.columns and 'gross' in data.columns:
            director_gross = data.groupby('director')['gross'].sum().nlargest(25)
            self.ax.barh(director_gross.index, director_gross.values,  color=random.choice(colors))
            self.ax.set_title('Directors by Gross Revenue', color='black')
            self.ax.set_ylabel('Director', color='black')
            self.ax.set_xlabel('Total Gross', color='black')
        else:
            self.missing_columns()
        self.canvas.draw()

    def budget_distribution(self):
        # budget distribution
        self.ax.clear()
        if 'budget' in data.columns:
            self.ax.hist(data['budget'], bins=30,  color=random.choice(colors), edgecolor='white')
            self.ax.set_title('Budget Distribution', color='black')
            self.ax.set_xlabel('Budget', color='black')
            self.ax.set_ylabel('Frequency', color='black')
            self.ax.grid(axis='y', linestyle=':', alpha=0.7)
        else:
            self.missing_columns()
        self.canvas.draw()

    def runtime_distribution(self):
        # plot of runtime distribution
        self.ax.clear()
        if 'runtime' in data.columns:
            self.ax.hist(data['runtime'].dropna(), bins=30,  color=random.choice(colors), edgecolor='white')
            self.ax.set_title('Runtime Distribution', color='black')
            self.ax.set_xlabel('Runtime (minutes)', color='black')
            self.ax.set_ylabel('Frequency', color='black')
        else:
            self.missing_columns()
        self.canvas.draw()

    def budget_revenue(self):
        self.ax.clear()
        if 'budget' in data.columns and 'gross' in data.columns:
            data_mean = data.groupby('year').agg({'budget': 'mean', 'gross': 'mean'}).reset_index()
            self.ax.plot(data_mean['year'], data_mean['budget'],label = 'budget')
            self.ax.plot(data_mean['year'], data_mean['gross'], label = 'gross')
            self.ax.set_title('Budget and Revenue Correlation through the years')
            self.ax.set_xlabel('Years')
            self.ax.set_ylabel('Money')
            self.ax.legend()
        else:
            self.missing_columns()
        self.canvas.draw()

    def preferred_genres(self):
        # plot of preferred genres
        self.ax.clear()
        if 'genre' in data.columns:
            preferred_genre = data['genre'].value_counts().nlargest(15)
            bars = self.ax.bar(preferred_genre.index, preferred_genre.values, color=random.choice(colors))
            for bar in bars:
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2, height + 15, str(height), ha='center', color='black')
            self.ax.set_title('Preferred Genres', color='black')
            self.ax.set_xlabel('Genre', color='black')
            self.ax.set_ylabel('Count', color='black')
        else:
            self.missing_columns()
        self.canvas.draw()

    def rating_popularity(self):
        self.ax.clear()
        if 'rating' in data.columns:
            rating_counts = data['rating'].value_counts().sort_values(ascending=False)
            self.ax.bar(rating_counts.index, rating_counts.values, color = random.choice(colors))
            self.ax.set_xlabel('Rating')
            self.ax.set_ylabel('Count')
            self.ax.set_title('Rating Distribution')
        else:
            self.missing_columns()
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())



