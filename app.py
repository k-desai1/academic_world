# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import mysql_utils
import mongodb_utils
import neo4j_utils
import warnings 

warnings.filterwarnings('ignore')

# Initiate DB connections
mysql = mysql_utils.connect_mysql()
mongo = mongodb_utils.connect_mongo()
neo4j = neo4j_utils.connect_neo4j()

# Incorporate data
query = "SELECT distinct name from university"
university_df = pd.read_sql(query, mysql)

query = "SELECT distinct name from keyword"
keyword_df = pd.read_sql(query, mysql)

query = "SELECT distinct name from faculty"
faculty_df = pd.read_sql(query, mysql)

# Initialize the app - incorporate a Dash Mantine theme
external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = html.Div([
    dbc.Row([dmc.Title('Academic World Discovery', color="blue", size="h3", style={'marginBottom': '10px'})]),
    html.Div(
        children=[
            html.Label('Keywords with the most Publications!', style={'font-size': '20px', 'font-weight': 'bold', 'display':'block'}),
            dcc.Slider(5, 25, 5, value=10, id='keyword-slider'),
            dcc.Graph(id='widget1-scatter')
        ], style={'width': '45%', 'display':'inline-block', 'margin-bottom': '10px', 'margin-right': '10px'}
    ),
    html.Div(
        children=[
            html.Label('Top Publications by Keyword!', style={'font-size': '20px', 'font-weight': 'bold', 'display':'block'}),
            dcc.Dropdown(keyword_df['name'], 'data mining', id='keyword-selector1', style={}), 
            dcc.Graph(id='widget2-scatter')
        ], style={'width': '45%', 'display':'inline-block', 'margin-bottom': '10px'}
    ),
    html.Div(
        children=[
            html.Label('Analyze University Keyword Relevance!', style={'font-size': '20px', 'font-weight': 'bold'}),
            dcc.Dropdown(university_df['name'], 'Stanford University', id='university-selector1', 
                            style={},
            ), 
            dcc.Graph(id='widget3-pie', style={'width': '40%', 'float': 'left'}),
            dcc.Graph(id='widget4-pie', style={'width': '40%', 'float': 'left'}),
        ], style={'width': '100%', 'display':'inline-block', 'margin-bottom': '10px', 'margin-right': '10px'}
    ),
    html.Div(
        children=[
            html.Label('Analyze Professors By Keyword!', style={'font-size': '20px', 'font-weight': 'bold'}),
            dcc.Dropdown(keyword_df['name'], 'genetic algorithm', id='keyword-selector2', 
                            style={},
            ), 
            html.P(id = "img-label"),
            html.Img(id='widget5-professor-pic', style={'height': '400px', 'width': '20%', 'float': 'left'}),
            dash_table.DataTable(id='widget6-table', style_table={'width': '20%'}),
        ], style={'width': '100%', 'display':'inline-block', 'margin-bottom': '10px', 'margin-right': '10px'}
    ),
    html.Div(
        children=[
            html.Label('Add Your Favorite Keywords:', style={'font-size': '20px', 'font-weight': 'bold', 'width':'50%'}),
            dcc.Input(id="add-keyword",type='text',placeholder='Input a keyword and press "ENTER" to add',debounce=True
                      , style={'width': '300px', 'marginLeft':'15px', 'marginRight': '15px'}),
            html.Label('Delete Your Favorite Keywords:', style={'font-size': '20px', 'font-weight': 'bold', 'width':'30%'}),
            dcc.Input(id="delete-keyword",type='text',placeholder='Input a keyword and press "ENTER" to delete',debounce=True
                      , style={'width': '300px', 'marginLeft':'15px', 'marginRight': '100px'}),
            html.Label('Favorite Keywords', style={'font-size': '20px', 'font-weight': 'bold', 'width':'30%', 'display':'inline-block'}),
            html.Label('Recommended Professors', style={'font-size': '20px', 'font-weight': 'bold', 'width':'30%', 'display':'inline-block'}),
            html.Label('Recommended Publications', style={'font-size': '20px', 'font-weight': 'bold', 'width':'40%', 'display':'inline-block'}),
            html.Div(children=[dash_table.DataTable(id='widget7-table', page_size=5)], style={'width': '25%', 'display':'inline-block', 'margin-right': '25px'}),
            html.Div(children=[dash_table.DataTable(id='widget8-table', page_size=5)], style={'width': '25%', 'display':'inline-block', 'margin-right': '25px'}),
            html.Div(children=[dash_table.DataTable(id='widget9-table', page_size=5, style_cell={"maxWidth": "750px"})], style={'width': '20%', 'display':'inline-block'}),
        ], style={'width': '100%', 'display':'inline-block', 'margin-bottom': '10px', 'margin-right': '10px'}
    ),
])

# Add controls to build the interaction
@callback(
    Output(component_id='widget1-scatter', component_property='figure'),
    Input(component_id='keyword-slider', component_property='value')
)
def update_widget1(num):
    query = """
        select k.name, count(distinct pk.publication_id) "publication count"
        from keyword k
        join publication_keyword pk
        on k.id = pk.keyword_id
        group by 1
        order by 2 desc
        limit %d
        """ % (num)
    df = pd.read_sql(query, mysql)
    figure=px.scatter(df, x="name", y="publication count", size=df["publication count"], color="name", log_y =True)
    return figure

@callback(
    Output(component_id='widget2-scatter', component_property='figure'),
    Input(component_id='keyword-selector1', component_property='value'),
)
def update_widget2(keyword):
    publications = mongo['publications']
    pipeline = [
        {'$match': { 'keywords.name': keyword } }, 
        {'$project': { '_id': 0, 'keywords': 1, 'numCitations': 1, 'title': 1 } }, 
        {'$unwind': "$keywords" }, 
        {'$match': { 'keywords.name': keyword } }, 
        {'$project': {'_id': 0, 'score': '$keywords.score', 'title':1, 'numCitations':1}},
        {'$sort': { 'numCitations': -1 }},
        {'$limit': 10}
    ]
    results = publications.aggregate(pipeline)   
    df = pd.DataFrame(list(results))
    figure=px.scatter(df, x="numCitations", y="score", size=df["numCitations"], color="title")
    return figure

@callback(
    Output(component_id='widget3-pie', component_property='figure'),
    Input(component_id='university-selector1', component_property='value'),
)
def update_widget3(university):
    faculty = mongo['faculty']
    pipeline = [
        {'$match': { 'affiliation.name': university } }, 
        {'$unwind': "$keywords" }, 
        {'$group': { '_id': "$keywords.name", 'faculty count': { '$sum': 1 } } },
        {'$sort': { 'faculty count': -1 }},
        {'$limit': 10}
    ]
    results = faculty.aggregate(pipeline)   
    df = pd.DataFrame(list(results))
    figure=px.pie(df, values='faculty count', names='_id', title='Popular Research Topics')
    return figure

@callback(
    Output(component_id='widget4-pie', component_property='figure'),
    Input(component_id='university-selector1', component_property='value'),
)
def update_widget4(university):
    query = """
        select keyword_name as name, count(distinct publication_id) "publication count"
        from publication_view
        where 
            university_name = '%s'
        group by 1
        order by 2 desc
        limit 10
        """ % (university)
    mysql = mysql_utils.connect_mysql()
    df = pd.read_sql(query, mysql)
    figure=px.pie(df, values='publication count', names='name', title='Popular Publication Topics')
    return figure

@callback(
    Output(component_id='widget5-professor-pic', component_property='src'),
    Output(component_id='img-label', component_property='children'),
    Output(component_id='widget6-table', component_property='data'),
    Input(component_id='keyword-selector2', component_property='value'),
)
def update_widget5(keyword):
    query = """
        select faculty_photo_url photo_url, faculty_id id, faculty_name name , count(distinct publication_id) publication_count
        from research_view
        where 
            keyword_name = '%s'
        group by 1, 2, 3
        order by 2 desc
        limit 1
        """ % (keyword)
    mysql = mysql_utils.connect_mysql()
    df = pd.read_sql(query, mysql)
    url = df['photo_url'][0]
    name = df['name'][0]
    id = df['id'][0]

    query = """
        select p.title, p.num_citations
        from faculty_publication fp
        join publication p
            on p.id = fp.publication_id
        where 
            fp.faculty_id = %s
        order by 2 desc
        limit 10
        """ % (id)
    mysql = mysql_utils.connect_mysql()
    df = pd.read_sql(query, mysql)  

    return url, name, df.to_dict('records')

@callback(
    Output(component_id='widget7-table', component_property='data', allow_duplicate=True),
    Output(component_id='add-keyword', component_property='value'),
    Output(component_id='widget8-table', component_property='data', allow_duplicate=True),
    Output(component_id='widget9-table', component_property='data', allow_duplicate=True),
    Input(component_id='add-keyword', component_property='value'),
    prevent_initial_call=True
)
def insert_widget7(keyword):
    mysql = mysql_utils.connect_mysql()
    if keyword is not None:
        if len(keyword.strip()) > 0:
            query = """
                    insert into favorite_keyword (id, name)
                    values (%s, %s)
                    """ 
            tuple = (None, keyword)
            print(tuple)
            cursor = mysql.cursor(prepared=True)
            cursor.execute(query, tuple)
            mysql.commit()
            print("Data inserted successfully!")
    query = """
        select distinct name as Keyword
        from favorite_keyword
        """
    mysql = mysql_utils.connect_mysql()
    df = pd.read_sql(query, mysql) 

    query = """
            MATCH (f:FACULTY) --> (k:KEYWORD)
            WHERE k.name in %s
            RETURN f.name AS `Faculty Name`
            """ % (df['Keyword'].values.tolist())
    faculty = neo4j.run(query)

    query = """
            MATCH (p:PUBLICATION) --> (k:KEYWORD)
            WHERE k.name in %s
            RETURN p.title AS `Publication Title`
            """ % (df['Keyword'].values.tolist())
    publication = neo4j.run(query)
    
    return df.to_dict('records'), '', faculty.data(), publication.data()

@callback(
    Output(component_id='widget7-table', component_property='data', allow_duplicate=True),
    Output(component_id='delete-keyword', component_property='value'),
    Output(component_id='widget8-table', component_property='data', allow_duplicate=True),
    Output(component_id='widget9-table', component_property='data', allow_duplicate=True),
    Input(component_id='delete-keyword', component_property='value'),
    prevent_initial_call=True
)
def delete_widget7(keyword):
    mysql = mysql_utils.connect_mysql()
    if keyword is not None:
        if len(keyword.strip()) > 0:
            query = """
                    delete from favorite_keyword
                    where name = %s
                    """ 
            cursor = mysql.cursor(prepared=True)
            try:
                cursor.execute(query, (keyword,))
                mysql.commit()
                print("Data successfully deleted! ")
            except mysql.connector.Error as error:
                print("parameterized query failed {}".format(error))
    query = """
        select distinct name as Keyword
        from favorite_keyword
        """
    mysql = mysql_utils.connect_mysql()
    df = pd.read_sql(query, mysql) 

    query = """
            MATCH (f:FACULTY) --> (k:KEYWORD)
            WHERE k.name in %s
            RETURN f.name AS `Faculty Name`
            """ % (df['Keyword'].values.tolist())
    faculty = neo4j.run(query)

    query = """
            MATCH (p:PUBLICATION) --> (k:KEYWORD)
            WHERE k.name in %s
            RETURN p.title AS `Publication Title`
            """ % (df['Keyword'].values.tolist())
    publication = neo4j.run(query)
    
    return df.to_dict('records'), '', faculty.data(), publication.data()

# Run the App
if __name__ == '__main__':
    app.run_server(debug=True)