# KaranDesai

**Title**: Academic World Discovery

**Purpose**:
* The *application scenario* is centered around keyword analytics, analyzing both publication topics and research topics from multiple different perspective by analyzing how keywords relate to faculty, publications, and universities. 
* The *target users* of this dashboard are potential research candidates.
* The *objectives* are to identify the most relevant faculty and universities to partner with and to help identify relevant publications in their area of interest (keyword)

**Demo**: https://mediaspace.illinois.edu/media/t/1_mvrzrwmr

**Installation**: 
* Clone code into local filesystem
* Make sure all DBs are running locally (mySQL, neo4j, and mongo)
* A new table 'FavoriteKeyword' is used for the bottom section of the dashboard, everything else on the dashboard uses the existing DBs and data we loaded as part of the MPs

**Usage**: 
* run the app.py file to start the webserver
* navigate to 'http://127.0.0.1:8050/'
* 1st widget (Keywords with the most Publications): the user can use the slider to look at most publicized keywords
* 2n widget (Top Publications by keyword): the user can select a keyword to look at top publications
* 3rd and 4th widgets (Popular Research and Publication Topics): the user can select a university to look at top publications and keywords
* 5th and 6th widgets (Analyze Professors by Keywords): the user select a keyword to look at the most cited faculty member for that topic
* 7th, 8th, and 9th widgets (Favorite Keywords, Recommended Professors, Recommended Publications): the user can add/remove favorite keywords to update the most relevant faculty and publications

**Design**:
* The dashboard runs on the three databases we set up in the MPs: mysql (academicworld), mongodb (academicworld), and neo4j (academicworld).
* I did create a new table in mysql(academic world) for the favorite keyword functionality
```sql
create table favorite_keyword( 
    id int not null auto_increment, 
    name varchar(512), 
    primary key(id) 
);

```
* The first component of the dash is the title 'Academic World Discovery' where I used the dash bootstrap components library to format it as a row and the dash mantime components to format the title as blue, H3, and set up some margins.
* The second component of the dash is the first widget (first row and first column) is made up of three components the label using html.Label, a slider input widget, and a scatter plot. The slider takes input of 5025 in increments of 5 and the scatter plot shows the top X keywords by the number of publications where X is set by the slider. This widget reads from mysql (academicworld) using the query defined in the callback function update_widget1 where the input is the number from the slider and the output is the top X keywords by publication count. 
* The third component of the dash is the second widget (first row and second column) is made up of three components the label using html.Label, a dropdown using of keywords, and a scatter plot. The dropdown is fed from the mysql (academicworld) a distinct list of keyword names from the keyword table. The scatter plot uses the callback function update_widget2 that takes input keyword from the dropdown and queries mongodb (academicworld) for the publications containing that keyword ordered by num_citations descending limited to the top10 for readability purposes.  
* The fourth component of the dash is a title textbox and dropdown that is powered by the list of university names from mysql. 
* The fifth component of the dash is a piechart widget powered by a callback function update_widget3 that listens to the university dropdown selector. This callback function takes the university name as input and returns the keywords with the most faculty members that have that keyword in their research topics. The results are limited to top 10. This widget reads from the mongodb faculty collection. 
* The sixth component of the dash is a piechart widget powered by a callback function update_widget4 that listens to the university dropdown selector. This callback function takes the university name as input and returns the keywords with the most publications associated with them. The results are limited to top 10. This widget reads from the mysql academicworld database. 
* The seventh component of the dash is a label and dropdown that is populated with the keyword names from the mysql db. 
* The eighth component of the dash is a combination of a img div tag and a datatable both powered by the keyword dropdown selector. When a user picks the keyword it returns a picture of the professor with the most publications and their top 10 most cited publications for that keyword. All of these is powered by the callback function update_widget5 and reads from mysql academicworld
* The ninth component of the dash is a label + text input box for adding favorite keywords. When the user types in a keyword and hits 'ENTER' it triggers the callback insert_widget7 that uses a prepared statement for inserting a new row in the favorite_keyword mysql table, and updates that last row of data tables (favorite keyword from mysql, recommended professors from neo4j, and recommended publications from neo4j)
* The tenth component of the dash is a label + text input box for deleting favorite keywords. When the user types in a keyword and hits 'ENTER' it triggers the callback delete_widget7 that uses a prepared statement for delete the favorite keyword in the favorite_keyword mysql table, and updates that last row of data tables (favorite keyword from mysql, recommended professors from neo4j, and recommended publications from neo4j) 
* The eleventh component of the dash (last row) is made up of three data tables powered by the add and delete keyword input textboxes. 

**Implementation**:
* The entire dashboard was built using python code. 
* The main function resides in the app.py python file and runs with the python app.py command to start the web server on localhost where the dashboard runs. 
* There are three separate utility modules that house each of the database connection constructors (mongodb_utils.py, mysql_utils.py, and neo4j_utils.py)
* For the mysql_utils.py I used the mysql library and specifically imported the connector object to manage all cursors used to read/update the database. 
* For the mongodb_utils.py I used the pymongo library and only needed the MongoClient object to manage all the cursors used to read from the mongodb, I did not build any functionality to update the mongoDB instance.
* For the neo4j_utils.py I used the neo4j library and imported the GraphDatabase object to manage all the read access functionality for neo4j, I did not build any functionality to update the neo4j db instance. 
* All three DB modules have the harcoded connection credentials and they all use root access to login into the respective instances -- not ideal because in real-life scenarios we should create an app specific login to be used by the webserver that is limited to read/insert/update/delete access and can't drop objects like user 'root'. Also credentials shouldn't be stored openly in code but probably saved in encrypted fashion somewhere in a filesystem. 
* In the main app.py the code is broken up into two sections: the app layout in the top half of the code and the callback functions in the bottom half of the code
- *Packages I used*: 
    - dash for all the html, table widgets, and callback functionality
    - dash_bootstrap_components for the dash title
    - pandas for reading/processing data from db's
    - plotly for the different charts
    - dash_mantine_componets for some formatting styles
    - warnings to suppress some noisy warnings from some of the db libraries
- *Code explanations*:
    - line 12 -- I suppress warnings
    - lines 14-17 I initiate all the db connections to be used in the callbacks
    - lines 19-27 I pull in the values that will populate the dropdowns for the dashboard
    - lines 29-31 I setup the ash mantine theme
    - lines 33-87 I layout the dashboard components using HTML Divs and a lot of different styling options to ensure we have a nice rectangular layout as required by the project specifications. (see design for more details on each widgets)
    - lines 89-302 I write all the callback functions for each of the widgets, I use a numbering scheme 1-n from left to right top to bottom. (see design for more details on each widgets)
    - lines 304-306 is the main function use to start the webserver

**Database Techniques**:
* Index -- I created three indices for this dashboard
1. First index was created on the 'name' attribute of the keyword table because we take keyword name input from the dashboard UI and it's going be used heavily in the WHERE clause in the backend. 
```sql
create index project_keyword on keyword(name);
```
2. Second index was created on the 'name' attribute of the university table because again it's one of the input values from the dashboard UI and can help speed up query performance. 
```sql
create index project_university on university(name);
```
3. Third index was created on the 'name' attribute of the new Favorite Keyword table I created because again we're using name to perform the add/delete operations in the dashboard. 
```sql
create index project_favorite on favorite_keyword(name);
```
* View -- I created a view for a few of the widgets that performed a join across a lot of different tables
1. This view was created for the top publication topics by keyword 
```sql
create view publication_view as 
    select  
        k.id as keyword_id,      
        k.name as keyword_name,     
        fp.publication_id as publication_id,     
        pk.score as score,
        f.id as faculty_id,     
        f.name as faculty_name,     
        f.position as faculty_position,     
        f.research_interest as faculty_research_interest,     
        f.email as faculty_email,     
        f.phone as faculty_phone,     
        f.photo_url as faculty_photo_url,
        u.id as university_id,     
        u.name as university_name,     
        u.photo_url as university_photo_url      
    from keyword k         
    join publication_keyword pk
        on k.id = pk.keyword_id         
    join faculty_publication fp             
        on pk.publication_id = fp.publication_id         
    join faculty f             
        on f.id = fp.faculty_id         
    join university u              
        on f.university_id = u.id;
```
2. This view was created for the top faculty research topics by keyword
```sql
create view research_view as
select 
	k.id as keyword_id, 
    k.name as keyword_name,
    fp.publication_id as publication_id,
    fk.score as score,
    f.id as faculty_id,
    f.name as faculty_name,
    f.position as faculty_position,
    f.research_interest as faculty_research_interest,
    f.email as faculty_email,
    f.phone as faculty_phone,
    f.photo_url as faculty_photo_url,
    u.id as university_id,
    u.name as university_name,
    u.photo_url as university_photo_url
    
from keyword k
join faculty_keyword fk
	on k.id = fk.keyword_id
join faculty_publication fp
	on fk.faculty_id = fp.faculty_id
join faculty f
	on f.id = fp.faculty_id
join university u 
	on f.university_id = u.id
```
* Prepared Statements
1. I used a prepared statement on the insert favorite keywords widgets you can see it in the app.py/insert_widget7 function and here's the code block below:
```python 
query = """
        insert into favorite_keyword (id, name)
        values (%s, %s)
        """ 
tuple = (str(id+1), keyword)
print(tuple)
cursor = mysql.cursor(prepared=True)
cursor.execute(query, tuple)
mysql.commit()
```
2. I also used another prepared statement on the delete operation for the favorite keywords you cna see it in the app.py/delete_widget7 function and here's the code block below:
```python
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
```


**Extra-Credit Capabilities**:
* Multi-database Querying: In the Add/Delete Favorite Keywords input widgets I built functionality that first performs the add/delete functionality in the mysql database -> then it returns the current list of favorite keywords from mysql -> sending that list as input to neo4j to get the recommended professors and publications.  

**Contribution**:
This was a solo project submission from Karan Desai. I would say it took about a total of 30 hours to develop the dashboard and most of the time was spent just getting the HTML layout polished up because all of the complex display layout options using CSS tags in the DIV elements.  