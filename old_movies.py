import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableView, QHeaderView
from PyQt5.QtCore import Qt, QAbstractTableModel

# Load and clean data
data = pd.read_csv('~/movies_analysis/movies.csv')
data.drop_duplicates(inplace=True)
data.dropna(inplace=True)

class PandasModel(QAbstractTableModel):
    def __init__(self, data_frame=pd.DataFrame()):
        super().__init__()
        self._data = data_frame

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
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

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data and Plot Viewer")
        self.setGeometry(100, 100, 1000, 800)

        # Set dark theme stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2e2e2e;
            }
            QPushButton {
                background-color: #444444;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QTableView {
                background-color: #3e3e3e;
                color: #ffffff;
                border: 1px solid #666666;
            }
            QHeaderView::section {
                background-color: #444444;
                color: #ffffff;
                padding: 5px;
            }
        """)

        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create buttons
        self.create_buttons()

        # Create a placeholder for DataFrame and plot
        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Initially show the DataFrame
        self.view_dataframe()

    def create_buttons(self):
        # Create buttons for various plots
        self.buttons = {
            "View DataFrame": self.view_dataframe,
            "Gross Plot": lambda: self.show_plot('gross'),
            "Rating Plot": lambda: self.show_plot('rating'),
            "Revenue by Country": self.plot_revenue_by_country,
            "Score by Country": self.plot_score_by_country,
            "Directors by Score & Revenue": self.plot_directors_score_revenue,
            "Directors by Score": self.plot_directors_score,
            "Directors by Gross": self.plot_directors_gross,
            "Budget Distribution": self.plot_budget_distribution,
            "Runtime Distribution": self.plot_runtime_distribution,
            "Release Date vs Revenue": self.plot_release_date_revenue,
            "Preferred Genres": self.plot_preferred_genres,
            "Top 10 Production Companies by Revenue": self.plot_top_production_companies,
            "Genres Popularity Over the Years": self.plot_genres_over_years,
            "Impact of Genre on Revenue": self.plot_genre_impact
        }

        # Add buttons to layout
        button_layout = QVBoxLayout()
        for text, func in self.buttons.items():
            btn = QPushButton(text)
            btn.clicked.connect(func)
            button_layout.addWidget(btn)
        self.layout.addLayout(button_layout)

    def setup_plot(self):
        """Sets up the plot with a dark theme."""
        self.ax.set_facecolor('#2e2e2e')
        self.figure.patch.set_facecolor('#2e2e2e')
        self.ax.tick_params(axis='both', colors='white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['bottom'].set_color('white')

    def plot_bar_chart(self, x, y, title, xlabel, ylabel, color, height_factor=1e7):
        """Plots a bar chart with optional text labels."""
        self.ax.clear()
        bars = self.ax.bar(x, y, color=color)
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2, height + height_factor, f'{height/1e6:.1f}M', ha='center', color='white')
        self.ax.set_title(title, color='white')
        self.ax.set_xlabel(xlabel, color='white')
        self.ax.set_ylabel(ylabel, color='white')
        self.ax.set_xticklabels(self.ax.get_xticklabels(), rotation=45, ha='right')
        self.canvas.draw()

    def view_dataframe(self):
        """Displays the DataFrame in the table view."""
        model = PandasModel(data)
        self.table_view.setModel(model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ax.clear()
        self.canvas.draw()

    def show_plot(self, plot_type):
        """Displays different types of plots based on the given type."""
        self.setup_plot()
        if plot_type == 'gross':
            self.plot_gross()
        elif plot_type == 'rating':
            self.plot_rating()

    def plot_gross(self):
        """Plot: Top 10 Highest Grossing Movies"""
        if 'gross' in data.columns:
            top_grossing = data.sort_values(by='gross', ascending=False).head(10)
            self.plot_bar_chart(top_grossing['name'], top_grossing['gross'], 'Top 10 Highest Grossing Movies', 'Movie Name', 'Gross Revenue (Billions)', 'lavender')
        else:
            self.ax.text(0.5, 0.5, 'No "gross" column in data', horizontalalignment='center', verticalalignment='center', color='white')
            self.canvas.draw()

    def plot_rating(self):
        """Plot: Rating Distribution"""
        if 'rating' in data.columns:
            self.ax.hist(data['rating'].dropna(), bins=30, color='#232F3E', edgecolor='black')
            self.ax.set_title('Rating Distribution', color='white')
            self.ax.set_xlabel('Rating', color='white')
            self.ax.set_ylabel('Count', color='white')
            self.canvas.draw()
        else:
            self.ax.text(0.5, 0.5, 'No "rating" column in data', horizontalalignment='center', verticalalignment='center', color='white')
            self.canvas.draw()

    def plot_top_production_companies(self):
        """Plot: Top 10 Production Companies by Revenue"""
        if 'production_companies' in data.columns and 'gross' in data.columns:
            top_companies = data.groupby('production_companies')['gross'].sum().nlargest(10)
            self.plot_bar_chart(top_companies.index, top_companies.values, 'Top 10 Production Companies by Revenue', 'Production Company', 'Total Revenue', 'purple')
        else:
            self.ax.text(0.5, 0.5, 'Missing required columns', horizontalalignment='center', verticalalignment='center', color='white')
            self.canvas.draw()

    def plot_genres_over_years(self):
        """Plot: Genres Popularity Over the Years"""
        if 'release_date' in data.columns and 'genres' in data.columns:
            data['release_year'] = pd.to_datetime(data['release_date']).dt.year
            genre_yearly = data.explode('genres').groupby(['release_year', 'genres']).size().unstack().fillna(0)
            genre_yearly.plot(ax=self.ax)
            self.ax.set_title('Genres Popularity Over the Years', color='white')
            self.ax.set_xlabel('Year', color='white')
            self.ax.set_ylabel('Number of Movies', color='white')
        else:
            self.ax.text(0.5, 0.5, 'Missing required columns', horizontalalignment='center', verticalalignment='center', color='white')
        self.canvas.draw()

    def plot_genre_impact(self):
        """Plot: Impact of Genre on Revenue"""
        if 'genres' in data.columns and 'gross' in data.columns:
            data['genres'] = data['genres'].apply(lambda x: x.split(',')[0])
            genre_impact = data.groupby('genres')['gross'].mean().nlargest(10)
            self.plot_bar_chart(genre_impact.index, genre_impact.values, 'Impact of Genre on Revenue', 'Genre', 'Average Revenue', 'skyblue')
        else:
            self.ax.text(0.5, 0.5, 'Missing required columns', horizontalalignment='center', verticalalignment='center', color='white')
        self.canvas.draw()

    def plot_revenue_by_country(self):
        """Plot: Revenue by Country"""
        if 'production_countries' in data.columns and 'gross' in data.columns:
            revenue_by_country = data.groupby('production_countries')['gross'].sum().nlargest(10)
            self.plot_bar_chart(revenue_by_country.index, revenue_by_country.values, 'Revenue by Country', 'Country', 'Total Revenue', 'orange')
        else:
            self.ax.text(0.5, 0.5, 'Missing required columns', horizontalalignment='center', verticalalignment='center', color='white')
        self.canvas.draw()

    def plot_score_by_country(self):
        """Plot: Score by Country"""
        if 'production_countries' in data.columns and 'rating' in data.columns:
            score_by_country = data.groupby('production_countries')['rating'].mean().nlargest(10)
            self.plot_bar_chart(score_by_country.index, score_by_country.values, 'Score by Country', 'Country', 'Average Score', 'lightgreen')
        else:
            self.ax.text(0.5, 0.5, 'Missing required columns', horizontalalignment='center', verticalalignment='center', color='white')
        self.canvas.draw()

    def plot_directors_score_revenue(self):
        """Plot: Directors by Score and Revenue"""
        if 'director' in data.columns and 'rating' in data.columns and 'gross' in data.columns:
            director_stats = data.groupby('director').agg({'rating': 'mean', 'gross': 'sum'}).nlargest(10, 'gross')
            self.ax.scatter(director_stats['rating'], director_stats['gross'], color='lightblue')
            for idx, (rating, revenue) in enumerate(zip(director_stats['rating'], director_stats['gross'])):
                self.ax.text(rating, revenue, f'{idx+1}', color='white')
            self.ax.set_title('Directors by Score and Revenue', color='white')
            self.ax.set_xlabel('Average Rating', color='white')
            self.ax.set_ylabel('Total Revenue', color='white')
        else:
            self.ax.text(0.5, 0.5, 'Missing required columns', horizontalalignment='center', verticalalignment='center', color='white')
        self.canvas.draw()

    def plot_directors_score(self):
        """Plot: Directors by Score"""
        if 'director' in data.columns and 'rating' in data.columns:
            director_score = data.groupby('director')['rating'].mean().nlargest(10)
            self.plot_bar_chart(director_score.index, director_score.values, 'Directors by Score', 'Director', 'Average Rating', 'salmon')
        else:
            self.ax.text(0.5, 0.5, 'Missing required columns', horizontalalignment='center', verticalalignment='center', color='white')
        self.canvas.draw()

    def plot_directors_gross(self):
        """Plot: Directors by Gross Revenue"""
        if 'director' in data.columns and 'gross' in data.columns:
            director_gross = data.groupby('director')['gross'].sum().nlargest(10)
            self.plot_bar_chart(director_gross.index, director_gross.values, 'Directors by Gross Revenue', 'Director', 'Total Revenue', 'cyan')
        else:
            self.ax.text(0.5, 0.5, 'Missing required columns', horizontalalignment='center', verticalalignment='center', color='white')
        self.canvas.draw()

    def plot_budget_distribution(self):
        """Plot: Budget Distribution"""
        if 'budget' in data.columns:
            self.ax.hist(data['budget'].dropna(), bins=30, color='lightcoral', edgecolor='black')
            self.ax.set_title('Budget Distribution', color='white')
            self.ax.set_xlabel('Budget', color='white')
            self.ax.set_ylabel('Frequency', color='white')
        else:
            self.ax.text(0.5, 0.5, 'Missing "budget" column', horizontalalignment='center', verticalalignment='center', color='white')
        self.canvas.draw()

    def plot_runtime_distribution(self):
        """Plot: Runtime Distribution"""
        if 'runtime' in data.columns:
            self.ax.hist(data['runtime'].dropna(), bins=30, color='lightgreen', edgecolor='black')
            self.ax.set_title('Runtime Distribution', color='white')
            self.ax.set_xlabel('Runtime (minutes)', color='white')
            self.ax.set_ylabel('Frequency', color='white')
        else:
            self.ax.text(0.5, 0.5, 'Missing "runtime" column', horizontalalignment='center', verticalalignment='center', color='white')
        self.canvas.draw()

    def plot_release_date_revenue(self):
        """Plot: Release Date vs Revenue"""
        if 'release_date' in data.columns and 'gross' in data.columns:
            data['release_date'] = pd.to_datetime(data['release_date'])
            self.ax.scatter(data['release_date'], data['gross'], color='lightcoral')
            self.ax.set_title('Release Date vs Revenue', color='white')
            self.ax.set_xlabel('Release Date', color='white')
            self.ax.set_ylabel('Gross Revenue', color='white')
            self.ax.tick_params(axis='x', rotation=45)
        else:
            self.ax.text(0.5, 0.5, 'Missing required columns', horizontalalignment='center', verticalalignment='center', color='white')
        self.canvas.draw()

    def plot_preferred_genres(self):
        """Plot: Preferred Genres"""
        if 'genres' in data.columns:
            genres = data.explode('genres')['genres'].value_counts()
            self.plot_bar_chart(genres.index, genres.values, 'Preferred Genres', 'Genre', 'Count', 'peachpuff')
        else:
            self.ax.text(0.5, 0.5, 'Missing "genres" column', horizontalalignment='center', verticalalignment='center', color='white')
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())

