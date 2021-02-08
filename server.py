from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import pyodbc

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-1RH354G;'
                      'Database=digiDB;'
                      'Trusted_Connection=yes;')




class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    _columns = {
        "digital_commodities": ["commodity_id", "name", "number_sold", "price", "number_in_store", "color", "weight",
                                "immediate_sending", "brand", "promotion_id"],
        "laptops": ["graphics", "cpu", "ram"],
        "mobiles": ["ram", "internal_storage", "os", "camera_resolution"],
        "case_covers": ["material", "size", "mobile", "mobile_os"],
        "assembled_cases": ["ram", "storage"],
        "computers_accessories": [],
        "external_hards": ["capacity"],
        "keyboards": ["connection_type", "background_light"],
        "monitors": ["screen_size", "resolution"],
        "phone_accessories": [],
        "phone_holder_bases": ["material"],
        "powerbanks": ["capacity", "number_ports"]
    }

    def do_GET(self):
        bits = urlparse(self.path)
        cursor, columns_names = self.database(self.parse_query(bits.query.split('&')))

        self.send_response(200)
        self.end_headers()

        html_string = self.fill_html_string(cursor , columns_names)
        self.wfile.write(bytes(html_string, "utf-8"))


    def do_POST(self):
        self.send_response(200)
        self.end_headers()

    def do_PUT(self):
        self.send_response(200)
        self.end_headers()

    def parse_query(self, query: list):
        if len(query) != 3:
            return -1

        type_value = query[0][5:]
        name_value = query[1][5:]
        immediate_value = query[2][10:]
        return {'type_value': type_value,
                'name_value': name_value,
                'immediate_value': immediate_value}

    def database(self, fields: dict):
        if  fields == -1:
            return -1 , -1
        cursor = conn.cursor()

        select_columns = ""
        select_columns_list = []
        for name in self._columns["digital_commodities"]:
            if name == "commodity_id":
                select_columns += " c."
            else:
                select_columns += " "
            select_columns += name + ","
            select_columns_list.append(name)

        for name in self._columns[fields["type_value"]]:
            select_columns += " " + name + ","
            select_columns_list.append(name)

        select_columns = select_columns[:-1]

        query = 'SELECT ' + select_columns + ' FROM digital_commodities c,' + fields['type_value'] + \
                ' v where c.commodity_id=v.commodity_id'

        #print(select_columns)

        if fields['name_value'] != "":
            query += " and c.name LIKE '%" + fields['name_value'] + "%'"

        if fields['immediate_value'] != 'None':
            query += ' and c.immediate_sending=' + fields['immediate_value']

        cursor.execute(query)
        return cursor, select_columns_list

    def fill_html_string(self, cursor , columns_names):
        if cursor == -1:
            return ''

        style_file = open("style.txt", "r") # read css file 
        html_string = "<html><head>" \
                      "<title>Digatal Database</title> "
        html_string += style_file.read()
        html_string += "</head>" \
                      "<body><table><thead><tr>"

        for node in columns_names:
            html_string += '<th>' + str (node) + '</th>'
        
        html_string += '</tr></thead><tbody>'
        
        for row in cursor:
            html_string += '<tr>'
            #html_string += str(row)
            for node in row:   
                html_string += '<td>' + str(node) + '</td>'
            html_string += '</tr>'


        html_string += "</tbody></table></body></html>"
        #print(html_string)
        return html_string







httpd = HTTPServer(('', 8080), SimpleHTTPRequestHandler)
print("waiting...")
httpd.serve_forever()
