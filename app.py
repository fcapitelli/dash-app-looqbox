# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
dfIMDB = pd.read_csv("imdb-data.csv")

# Filtering genre
arrGenre = dfIMDB["Genre"].unique()

# Creating a genre list
genreSet = set()
for i in range(len(arrGenre)-1):
    temp = arrGenre[i].split(sep=",")
    for j in range(len(temp)-1):
        genreSet.add(temp[j])
        
# Creating main dataframe
yearList = dfIMDB["Year"].unique()
yearList.sort()
genreYear = []
genreName = []
genreAmount = []
genreRating = []
genreMetascore = []
genreRevenue = []
for year in yearList:
    for genre in genreSet:
        genreYear.append(year)
        genreName.append(genre)
        genreAmount.append(dfIMDB["Genre"].loc[dfIMDB["Year"] == year].str.count(genre).sum())
        genreRating.append(dfIMDB["Rating"].loc[(dfIMDB["Year"] == year) & (dfIMDB["Genre"].str.contains(genre))].mean())
        genreMetascore.append(dfIMDB["Metascore"].loc[(dfIMDB["Year"] == year) & (dfIMDB["Genre"].str.contains(genre))].mean())
        genreRevenue.append(dfIMDB["RevenueMillions"].loc[dfIMDB["Year"] == year].loc[dfIMDB["Genre"].str.contains(genre)].sum())
dfGenreByYear = pd.DataFrame(list(zip(genreYear, genreName, genreAmount, genreRating, genreMetascore, genreRevenue)), columns=["Year", "Genre", "Total", "Avg_Rating", "Avg_Metascore", "Total_RevenueMillions"])
dfGenreByYear.dropna(inplace=True)     

# Create a dash application
app = dash.Dash(__name__)
server = app.server

# Create an app layout
app.layout = html.Div(style={'font-family': 'sans-serif'}, children=[html.H1('Looqbox Data Challenge Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40, 'font-family': 'sans-serif'}),
                                # Year dropdown                                     
                                html.P("Release Year:", style={'font-size':15, 'font-weight': 'bold'}),
                                dcc.Dropdown(id='year-dropdown',
                                             options=[{'label': 'All Years', 'value': 'ALL'},
                                                      {'label': '2006', 'value': '2006'},
                                                      {'label': '2007', 'value': '2007'},
                                                      {'label': '2008', 'value': '2008'},
                                                      {'label': '2009', 'value': '2009'},
                                                      {'label': '2010', 'value': '2010'},
                                                      {'label': '2011', 'value': '2011'},
                                                      {'label': '2012', 'value': '2012'},
                                                      {'label': '2013', 'value': '2013'},
                                                      {'label': '2014', 'value': '2014'},
                                                      {'label': '2015', 'value': '2015'},
                                                      {'label': '2016', 'value': '2016'},
                                                      ],
                                             value='ALL',
                                             placeholder='Select a Release Year',
                                             searchable=True
                                             ),
                                html.Br(),
                                # Chart div
                                html.Div([
                                    html.Div(dcc.Graph(id='genre-pie-chart'), style={'width': '50%'}),
                                    html.Div(dcc.Graph(id='revenue-by-genre-column-chart'), style={'width': '50%'})
                                    ], style={'display': 'flex', 'width':'100% !important'}),
                                html.Br(),
                                # Chart div
                                html.Div(dcc.Graph(id='top10-revenue-bar-chart')),
                                ])

# Callback function
@app.callback([
              Output(component_id='genre-pie-chart', component_property='figure'),
              Output(component_id='revenue-by-genre-column-chart', component_property='figure'),
              Output(component_id='top10-revenue-bar-chart', component_property='figure')
              ],
              Input(component_id='year-dropdown', component_property='value'))

def get_chart(selected_year):
    
    nCat = 7 #definir o número de categorias que o gráfico será dividido
    dfGenreByYearPie = dfGenreByYear.copy(deep=True)
    colors = genreSet
    
    if selected_year == 'ALL':
        
        #Pie_chart
        filtered_df = dfGenreByYearPie.groupby("Genre", as_index=False).sum().sort_values(by="Total", ascending=False).copy(deep=True)
        filtered_df.reset_index(drop=True, inplace=True)
        nLimitOthers = filtered_df.iloc[nCat-2]["Total"]
        filtered_df2 = filtered_df.copy(deep=True)
        filtered_df.loc[filtered_df["Total"] < nLimitOthers, "Genre"] = "Other genres"
        
        labels = filtered_df["Genre"]
        values = filtered_df["Total"]
        
        fig_pie_chart = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0.1, 0, 0, 0, 0, 0, 0], opacity=0.85, titleposition="top left")])
        fig_pie_chart.update_traces(textposition='outside', textinfo='percent+label', marker=dict(line=dict(color="#FFFFFF", width=1)))
        fig_pie_chart.update_layout(title='Movies by Genre (All Years)')
        
        #Revenue_by_genre_chart
        fig_revenue_by_genre_chart = px.bar(filtered_df2,
                                            x="Genre",
                                            y="Total_RevenueMillions",
                                            color="Genre",
                                            title="Revenue by Genre (All Years)",
                                            labels={"Total_RevenueMillions": "Total Revenue (Millions $USD)"})
        fig_revenue_by_genre_chart.update_layout(xaxis={'categoryorder':'total descending'})
        
        #Top10_movie_by_year
        top10ProfitableMovies = dfIMDB.sort_values(by="RevenueMillions", ascending=False).head(10)
        fig_top10_movie = px.bar(top10ProfitableMovies, x="RevenueMillions", y="Title", labels={"Title": "", "RevenueMillions": "Revenue (Millions $USD)"}, opacity=0.85, color="RevenueMillions", color_continuous_scale=[(0, "#C6DDFF"), (1, "#1A76FF")])
        fig_top10_movie.update_layout(yaxis={'categoryorder':'total ascending'}, title='Top 10 Most Profitable Movies by Year (All Years)', title_x=0.5, showlegend=False)
        
        
        return [fig_pie_chart, fig_revenue_by_genre_chart, fig_top10_movie]
    else:
        
        #Pie_chart
        filtered_df = dfGenreByYearPie.query('Year == {}'.format(selected_year))
        filtered_df.sort_values("Total", ascending=False, inplace=True)
        nLimitOthers = filtered_df["Total"].iloc[nCat-2]
        filtered_df2 = filtered_df.copy(deep=True)
        filtered_df.loc[filtered_df["Total"] < nLimitOthers, "Genre"] = "Other genres"
        
        labels = filtered_df["Genre"]
        values = filtered_df["Total"]
        
        fig_pie_chart = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0.1, 0, 0, 0, 0, 0, 0], opacity=0.85, titleposition="top left")])
        fig_pie_chart.update_traces(textposition='outside', textinfo='percent+label', marker=dict(line=dict(color="#FFFFFF", width=1)))
        fig_pie_chart.update_layout(title='Movies by Genre ({})'.format(selected_year))
        
        #Revenue_by_genre_chart
        fig_revenue_by_genre_chart = px.bar(filtered_df2,
                                            x="Genre",
                                            y="Total_RevenueMillions",
                                            color="Genre",
                                            title="Revenue by Genre ({})".format(selected_year),
                                            labels={"Total_RevenueMillions": "Total Revenue (Millions $USD)"})
        fig_revenue_by_genre_chart.update_layout(xaxis={'categoryorder':'total descending'})
        
        #Top10_movie_by_year
        top10ProfitableMovies = dfIMDB.query('Year == {}'.format(selected_year))
        top10ProfitableMovies = top10ProfitableMovies.sort_values(by="RevenueMillions", ascending=False).head(10)
        fig_top10_movie = px.bar(top10ProfitableMovies, x="RevenueMillions", y="Title", labels={"Title": "", "RevenueMillions": "Revenue (Millions $USD)"}, opacity=0.85, color="RevenueMillions", color_continuous_scale=[(0, "#C6DDFF"), (1, "#1A76FF")])
        fig_top10_movie.update_layout(yaxis={'categoryorder':'total ascending'}, title='Top 10 Most Profitable Movies by Year ({})'.format(selected_year), title_x=0.5, showlegend=False)
        return [fig_pie_chart, fig_revenue_by_genre_chart, fig_top10_movie]
            
            

# Run the app
if __name__ == '__main__':
    app.run_server()