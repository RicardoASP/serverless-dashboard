import pandas as pd
import sqlite3

class DashboardItems():
    engine = sqlite3.connect("D:/Projects/sandbox/serverless_dashboard/dataset/netflix.db")

    def navbar(self):
        navbar_template = """
        <nav class="navbar navbar-expand-lg navbar-light bg-danger">
          <a class="navbar-brand" href="#"><img src="D:/Projects/sandbox/serverless_dashboard/netflix-logo.png" width="100px"/></a>
          <div class="collapse navbar-collapse" id="navbarText">
            <ul class="navbar-nav mr-auto">
              <li class="nav-item active">
                <a class="nav-link text-white" href="#">Home <span class="sr-only">(current)</span></a>
              </li>
              <li class="nav-item">
                <a class="nav-link text-white" href="#">View 2</a>
              </li>
              <li class="nav-item">
                <a class="nav-link text-white" href="#">View 3</a>
              </li>
            </ul>
            <span class="navbar-text">
                <h4 style="color:white;"><b>SERVERLESS DASHBOARD</b></h4>
            </span>
          </div>
        </nav>
        """

        return navbar_template

    def graph1(self):
        conn = self.engine
        sql= """SELECT 
                type,
                ltrim(substr(date_added, length(date_added)-4, length(date_added)),' ') || "-" || 
                CASE
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'January' THEN '01'
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'February' THEN '02'
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'March' THEN '03'
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'April' THEN '04'
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'May' THEN '05'
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'June' THEN '06'
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'July' THEN '07'
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'August' THEN '08'
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'September' THEN '09'
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'October' THEN '10'
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'November' THEN '11'
                    WHEN substr(ltrim(date_added,' '),0, instr(ltrim(date_added),' ')) = 'December' THEN '12'
                END AS date_added,
                count(*) as item_count
                FROM MOVIES
                WHERE date_added IS NOT NULL 
                GROUP BY 1,2
                ORDER BY 2 ASC;"""
        combine_dataset = pd.read_sql(sql,conn).values.tolist()
        tv_shows = []
        movies = []
        for dataset in combine_dataset:
            if dataset[0] == "TV Show":
                tv_shows.append(dataset)
            elif dataset[0] == "Movie":
                movies.append(dataset)

        tv_data_points = ''
        for tv_show in tv_shows:
            tv_data_point = '{label:' + '"' + tv_show[1] + '", y:' + str(tv_show[2]) + '},'
            tv_data_points = tv_data_points + tv_data_point

        movie_data_points = ''
        for movie in movies:
            movie_data_point = '{label:' + '"' + movie[1] + '", y:' + str(movie[2]) + '},'
            movie_data_points = movie_data_points + movie_data_point

        #region --chart1 template
        chart1_template = """
                var chart = new CanvasJS.Chart("chart_1", {
                    animationEnabled: true,
                    title:{
                        text: "Movies/TV Shows Inventory by Release Date"
                    },
                    axisY: {
                        title: "Quantity",
                        maximun: 250,
                        interval: 50
                    },
                    legend:{
                        cursor: "pointer",
                        fontSize: 16,
                        itemclick: toggleDataSeries
                    },
                    toolTip:{
                        shared: true
                    },
                    data: [{
                        name: "TV Shows",
                        type: "spline",
                        showInLegend: true,
                        dataPoints: [
                           """ + tv_data_points[0:-1] + """
                        ]
                    },
                    {
                        name: "Movies",
                        type: "spline",
                        showInLegend: true,
                        dataPoints: [
                            """ + movie_data_points[0:-1] + """
                        ]
                    }]
                });
                chart.render();

                function toggleDataSeries(e){
                    if (typeof(e.dataSeries.visible) === "undefined" || e.dataSeries.visible) {
                        e.dataSeries.visible = false;
                    }
                    else{
                        e.dataSeries.visible = true;
                    }
                    chart.render();
                }
        """
        #endregion

        return chart1_template

    def graph2(self):
        conn= self.engine
        sql = """
        SELECT listed_in
        FROM movies
        """
        dataset = pd.read_sql(sql, conn).values.tolist()
        cat_freq = []
        for row in dataset:
            cat_list = row[0].split(',')
            for cat in cat_list:
                cat_freq.append(cat.strip())

        unique_cats = []
        for x in cat_freq:
            if x not in unique_cats:
                unique_cats.append(x)

        data_points = ""
        for unique_cat in unique_cats:
            data_points = data_points + '{label:"' + str(unique_cat) + '", y: ' + str(cat_freq.count(unique_cat)) + '},'

        chart2_template = """
        var chart = new CanvasJS.Chart("chart_2", {
                animationEnabled: true,
                exportEnabled: true,
                theme: "light1", // "light1", "light2", "dark1", "dark2"
                title:{
                    text: "Total Inventory by Category"
                },
                axisY: {
                  includeZero: true
                },
                data: [{
                    type: "column", //change type to bar, line, area, pie, etc
                    indexLabel: "{y}", //Shows y value on all Data Points
                    indexLabelFontColor: "#5A5757",
                    indexLabelFontSize: 10,
                    indexLabelPlacement: "outside",
                    dataPoints: [
                        """ + data_points[0:-1] + """
                        ]
                    }]
                });
                chart.render();
        """
        return chart2_template

    def table(self):
        conn = self.engine
        sql = """
                SELECT director, type, count(*) as rec_count
                FROM movies
                WHERE director is not Null
                GROUP BY 1,2
                ORDER BY count(*) DESC
                LIMIT 100
            """
        dataset = pd.read_sql(sql, conn).values.tolist()
        table_rows = ""
        for row in dataset:
            table_row = ""
            for item in row:
                table_row = table_row + "<td>" + str(item) + "</td>"
            table_rows = table_rows + "<tr>" + table_row + "</tr>"

        table = f"""
        <table class="table table-bordered">
              <thead>
                <tr>
                  <th scope="col">Director</th>
                  <th scope="col">Type</th>
                  <th scope="col">Quantity</th>
                </tr>
              </thead>
              <tbody>
                {table_rows}
              </tbody>
          </table>
        """

        return table

def html_template(navbar, chart1, chart2, table):
    #region --html template
    html_template = """
    <!DOCTYPE html>
    <html lang="en" dir="ltr">
    <head>
        <!-- bootstrap libraries-->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
              integrity="sha384-JcKb8q3iqJ61gNV9KGb8thSsNjpSL0n8PARn9HuZOnIxN0hoP+VmmDGMN5t9UJ0Z" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"
                integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj"
                crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"
                integrity="sha384-9/reFTGAW83EW2RDu2S0VKaIzap3H66lZH81PoYlFhbGU+6BZp6G7niu735Sk7lN"
                crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"
                integrity="sha384-B4gt1jrGC7Jh4AgTPSdUtOBvfO8shuf57BaghqFfPlYxofvL8/KUEfYiJOMMV+rV"
                crossorigin="anonymous"></script>

        <!-- canvasjs libraries -->
        <script src="https://canvasjs.com/assets/script/canvasjs.min.js"></script>
        <script type="text/javascript">
            window.onload = function () {""" + chart1 + """ """ + chart2 + """}""" + f"""</script>
        <link rel="icon" type="image/png" href="D:/Projects/sandbox/serverless_dashboard/favicon.png">
        <meta charset="utf-8">
        <title>Stakeholders Dashboard</title>
    </head>
    <body>
    <!-- navbar block -->
        """ + navbar + f"""
    <!-- end navbar block -->

    <div class="divider" style="margin-top:40px;"></div>

    <div class="container">
      <div class="row">
          <div class="col">
            <div id="chart_1" style="height: 370px; width: 100%;"></div>
        </div>
      </div>

      <div class="divider" style="margin-top:40px;"></div>

      <div class="row">
        <div class="col">
          <div id="chart_2" style="height: 370px; width: 100%;"></div>
        </div>
        <div class="col">
          <h3>Best Directors Based on Ratings</h3>
          <div style="overflow-y: scroll; height: 350px;">
          { table }
          </div>
        </div>
      </div>
    </div>

    </body>
    </html>
    """
    #endregion
    return html_template

#initiate class
items= DashboardItems()()

#create html page
html_file = html_template(items.navbar(), items.graph1(), items.graph2(), items.table())

#output html page in the right path
path="D:/Projects/sandbox/serverless_dashboard/netflix-dashboard.html"

with open(path, "w", encoding="utf-8") as f:
    f.write(html_file)