import os
from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, IMAGES
import simplejson as json
import psycopg2
from werkzeug.utils import secure_filename

""" Macros for relation and column names """
client_table_name = "\"Client\""
client_client_id_col = "\"ClientID\""
client_client_rating_col = "\"Client Rating\""

client_ratings_table_name = "\"Client Ratings\""
client_ratings_client_id_col = "\"ClientID\""
client_ratings_reviewer_id_col = "\"ReviewerID\""
client_ratings_comments_col = "\"Comments\""
client_ratings_rating_col = "\"Rating\""

cook_table_name = "\"Cook\""
cook_cook_id_col = "\"CookID\""
cook_cook_rating_col = "\"Cook Rating\""

cook_ratings_table_name = "\"Cook Rating\""
cook_ratings_cook_id_col = "\"CookID\""
cook_ratings_reviewer_id_col = "\"ReviewerID\""
cook_ratings_comments_col = "\"Comments\""
cook_ratings_rating_col = "\"Rating\""

listing_table_name = "\"Listing\""
listing_listing_id_col = "\"ListingID\""
listing_cook_id_col = "\"CookID\""
listing_food_name_col = "\"Food Name\""
listing_price_col = "\"Price\""
listing_location_col = "\"Location\""
listing_image_col = "\"Image\""
listing_active_col = "\"active\""

listing_tags_table_name = "\"Listing Tags\""
listing_tags_listing_id_col = "\"ListingID\""
listing_tags_tag_col = "\"Tag\""

order_table_name = "\"Order\""
order_client_id_col = "\"ClientID\""
order_listing_id_col = "\"ListingID\""
order_status_col = "\"Status\""
order_time_of_order_col = "\"Time of Order\""

user_table_name = "\"User\""
user_user_id_col = "\"UserID\""
user_password_col = "\"Password\""
user_fname_col = "\"FName\""
user_lname_col = "\"LName\""
user_about_col = "\"About\""


""" Database login details """
db_host = "redacted"
db_name = "redacted"
db_user = "redacted"
db_password = "redacted"

conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
app = Flask(__name__)


photos = UploadSet('photos', IMAGES)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
UPLOAD_DIR         = '/home/ubuntu/project-team-07/backend-api/images'
app.config['UPLOAD_DIR'] = UPLOAD_DIR

##################################################
def removeQuotes(stringy):
    """ Removes the first and last characters (double quotes) from a string, and then return it """
    return stringy.replace("\"", "")

# --------------------------------------------------- UPLOAD IMAGES ---------------------------------------------------#


@app.route("/api/uploadImage", methods=['GET', 'POST'])
def uploadImages():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            max_listing_id=getListId()-1
            filename = str(max_listing_id)+".jpg"
            file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
    return "success"


# Make sure extension is in the ALLOWD_EXTENSIONS set
def check_extension(extension):
    return extension in ALLOWED_EXTENSIONS

# --------------------------------------------------- GET IMAGES ---------------------------------------------------#


@app.route("/api/getImage/<int:listId>", methods=['GET'])
def getImages(listId):
    with open("/home/ubuntu/project-team-07/backend-api/images/"+str(listId)+".jpg", "rb") as imageFile:
        f = imageFile.read()
        b = bytearray(f)
        return b
    return "failed"


# --------------------------------------------------- GET COOK LISTING ---------------------------------------------------#


@app.route("/api/getCookListing/<int:userId>", methods=['GET'])
def get_cook_id(userId):
    try:
        all_orders = []

        search_all = conn.cursor()

        search_all.execute(
            "SELECT * FROM {} WHERE ({} = {})".format(listing_table_name, listing_cook_id_col, str(userId)))

        single_row = search_all.fetchone()

        while single_row is not None:
            all_orders.append(single_row)
            single_row = search_all.fetchone()

        search_all.close()

        rows_to_json(all_orders)  # want to convert each row into a JSON string

        return json.dumps({'data': all_orders})  # convert to string before returning
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()
        
  
# --------------------------------------------------- GET USER DETAIL ---------------------------------------------------#


@app.route("/api/getUserDetails/<int:userId>", methods=['GET'])
def get_user_detail(userId):
    try:
        all_details = []

        search_all = conn.cursor()

        search_all.execute(
            "SELECT * FROM {} WHERE ({} = {})".format(user_table_name, user_user_id_col, str(userId)))

        single_row = search_all.fetchone()

        while single_row is not None:
            all_details.append(single_row)
            single_row = search_all.fetchone()

        search_all.close()

        user_detail_rows_to_json(all_details)  # want to convert each row into a JSON string

        return json.dumps({'data': all_details})  # convert to string before returning
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()
 

def user_detail_rows_to_json(rows):
    """
    Mutate rows such that each tuple in rows is converted to a JSON string representing the same information.
    """
    for i in range(len(rows)):
        rows[i] = json.dumps({'UserID': rows[i][0],
                              'Password': rows[i][1],
                              'FName': rows[i][2],
                              'LName': rows[i][3],
                              'About': rows[i][4]})
       

# --------------------------------------------------- GET ALL LISTINGS ---------------------------------------------------#
@app.route('/api/getAllListings', methods=['GET'])
def getAllListings():
    all_rows = []

    try:
        search_all = conn.cursor()
        search_all.execute("SELECT {}, {}, {}, {},"
                           " {}, {}, {} FROM public.{}".format(listing_listing_id_col,
                                                           listing_cook_id_col,
                                                           listing_food_name_col,
                                                           listing_price_col,
                                                           listing_location_col,
                                                           listing_image_col,
                                                               listing_active_col,
                                                           listing_table_name))
        single_row = search_all.fetchone()

        while single_row is not None:
            all_rows.append(single_row)
            single_row = search_all.fetchone()

        search_all.close()

        rows_to_json(all_rows)  # want to convert each row into a JSON string

        return json.dumps({'data': all_rows})  # convert to string before returning

    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()

    # single_row = search_all.fetchone()
    #
    # while single_row is not None:
    #     all_rows.append(single_row)
    #     single_row = search_all.fetchone()
    #
    # search_all.close()
    #
    # rows_to_json(all_rows)  # want to convert each row into a JSON string
    #
    # return json.dumps({'data': all_rows})  # convert to string before returning


# --------------------------------------------------- ADD LISTING ---------------------------------------------------#

@app.route('/api/add', methods=['GET', 'POST'])
def addReq():
    if request.method == "GET":
        return printTables()
    elif request.method == "POST":
        addToDB(request.get_json())
        conn.commit()
        return "Success"


def encase_in_quotes(stringy):
    return "\"" + stringy + "\""


"""
Adds the Listing entry to the PSQL database with the given JSONdata
JSON format is a dictionary where the keys are the column names of the listing, along with
a key "tagList" which is a list of tags:
"""


def addToDB(json_data):
    cur = conn.cursor()
    json_dict = json_data

    list_id = getListId()
    cook_id = json_dict[removeQuotes(listing_cook_id_col)]
    food_name = json_dict[removeQuotes(listing_food_name_col)]
    price = json_dict[removeQuotes(listing_price_col)]
    loc = json_dict[removeQuotes(listing_location_col)]
    image = json_dict[removeQuotes(listing_image_col)]
    tags = json_dict["tags"]
    print(tags)
    
    sql = "INSERT INTO " + listing_table_name + " VALUES (%s, %s, %s, %s, %s, %s, TRUE)"
    try:
        cur.execute(sql, (list_id, cook_id, food_name, price, loc, image))
        addTags(tags, list_id)
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()

    # addTags(tags, list_id)


def addTags(tag_list, listing_id):
    """
    Adds a list of tags tag_list for a given listing with listing_id to the database
    """
    cur = conn.cursor()
    for x in tag_list:
        sql = "INSERT INTO " + listing_tags_table_name + " VALUES (%s , %s)"
        try:
            cur.execute(sql, (listing_id, removeQuotes(x)))
        except:
            rollback = conn.cursor()
            rollback.execute("ROLLBACK")
            rollback.commit()


def getListId():
    """ Returns an unused listing_id """
    cur = conn.cursor()
    sql = "SELECT max({}) FROM {}".format(listing_listing_id_col,
                                          listing_table_name)
    try:
        cur.execute(sql)
        maxID = cur.fetchone()
        if maxID[0] == None:
            return 1
        else:
            return maxID[0] + 1
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()

    # maxID = cur.fetchone()
    # if maxID[0] == None:
    #     return 1
    # else:
    #     return maxID[0] + 1


def printTables():
    try:
        cur = conn.cursor()
        strout = "--------------------------ListingTable---------------------------<br>"
        sql = "SELECT * FROM {}".format(listing_table_name)
        cur.execute(sql)
        listings = cur.fetchall()
        for x in listings:
            for y in x:
                strout = strout + str(y) + "|| "
            strout = strout + "<br>"
        sql = "SELECT * FROM {}".format(listing_tags_table_name)
        cur.execute(sql)
        listings = cur.fetchall()
        strout += "<br><br><br>--------------------------TagTable-------------------------<br>"
        for x in listings:
            for y in x:
                strout = strout + str(y) + "   "

            strout = strout + "<br>"
        return strout
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()


# --------------------------------------------------- CANCEL ---------------------------------------------------#


@app.route('/api/cancel/<int:clientId>/<int:listingId>', methods=['GET'])
def cancel(clientId, listingId):
    """
    Cancels the order with specified client id and listing id and returns it.
    returns 'order not found' if the client id and listing id do not exist as a key or if the listing has already
    been canceled or fulfilled.
    """

    in_progress = get_in_progress_order(clientId, listingId)

    if in_progress:
        cancel_order(clientId, listingId)
        output = order_to_json(in_progress)  # want to convert each row into a JSON string

        return "Success"  # convert to string before returning
    else:
        return 'Failed'


def get_in_progress_order(clientId, listingId):
    """
    Return the in progress order that corresponds with ClientId and ListingID
    """
    try:
        matched_rows = []

        order = conn.cursor()
        order.execute(
            "SELECT t1.\"ClientID\", t1.\"ListingID\", t1.\"Status\", t1.\"Time of Order\" from public.\"Order\""
            " as t1 WHERE t1.\"ClientID\" = " + str(clientId) + " AND \"ListingID\" = " + str(listingId) +
            " AND t1.\"Status\" = \'Pending\'")

        order_row = order.fetchone()

        while order_row is not None:
            matched_rows.append(order_row)
            order_row = order.fetchone()

        order.close()

        return matched_rows
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()


def cancel_order(clientId, listingId):
    """
    given a clientId and listingId cancel the order in progress associated with them
    """
    try:
        order = conn.cursor()
        order.execute(
            "UPDATE public.\"Order\" SET \"Status\" = 'Canceled' WHERE \"ClientID\" = " + str(clientId) +
            " AND \"ListingID\" = " + str(listingId) + " AND \"Status\" = \'Pending\'")
        conn.commit()

        order.close()
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()


def order_to_json(rows):
    """
    Takes in a list of tupples for the Orders schema and returns a json formated representation of the data.
    """
    string = ""
    for i in range(len(rows)):
        string += json.dumps({'ClientID': rows[i][0],
                              'ListingID': rows[i][1],
                              'Status': rows[i][2],
                              'DateTime': rows[i][3].__str__()})
        if i != len(rows) - 1:
            string += ","

    return string


# --------------------------------------------------- getOrderStatus ---------------------------------------------------#


@app.route('/api/getOrderStatus/<int:clientId>/<int:listingId>', methods=['GET'])
def getOrderStatus(clientId, listingId):
    """
    Retruns a list of jsons representing tupples in the Orders table for the given client
    """

    in_progress = queryOrderUsingClientID(clientId, listingId)

    output = order_to_json(in_progress)  # want to convert each row into a JSON string

    return output  # convert to string before returning


def queryOrderUsingClientID(clientId, listingId):
    """
    Return a list of Order tuples belonging to the client with the given id.
    """
    try:
        matched_rows = []

        orders = conn.cursor()
        orders.execute(
            "SELECT t1.\"ClientID\", t1.\"ListingID\", t1.\"Status\", t1.\"Time of Order\" from public.\"Order\""
            " as t1 WHERE t1.\"ClientID\" = " + str(clientId) + " AND \"ListingID\" = " + str(listingId))

        order_row = orders.fetchone()

        while order_row is not None:
            matched_rows.append(order_row)
            order_row = orders.fetchone()

        orders.close()

        return matched_rows
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()


# --------------------------------------------------- MARK AS COMPLETE ---------------------------------------------------#


completed = "\'Completed\'"


@app.route("/api/markComplete/<int:clientID>/<int:listingID>", methods=['GET'])
def mark_as_complete(clientID, listingID):
    """ A function that changes the status of the order with listing id listing_id to complete.
        Returns "Success" on a sucessful change of the listing id's order to complete.
        @param clientID: the client id number to change the status.
        @param listingID: the listing id number to change the status.
        @rtype: str
    """

    sql = \
        """
            UPDATE public.{}
            SET {} = {}
            WHERE {} = {} AND {} = {}
        """.format(order_table_name, order_status_col, completed, order_listing_id_col, str(listingID),
                   order_client_id_col, str(clientID))

    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        if cur.rowcount == 0:  # do we put this here?
            raise Exception(
                "The status of listing id's order was not changed. ClientID or ListingID may be out of range.")
        return "Success"
    # except Exception as e: #### THIS WAS HERE PREVIOUSLY
    #     raise Exception(e)
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()

    # Check to see if a row in the database has been updated.
    # if cur.rowcount == 0:
    #     raise Exception("The status of listing id's order was not changed. ClientID or ListingID may be out of range.")
    # return "Success"


# --------------------------------------- MARK AS IN PROGRESS --------------------------------------#

@app.route('/api/updateOrderStatusToInProgress/<int:clientID>/<int:listingID>', methods=['GET'])
def updateOrderStatusToInProgress(clientID, listingID):
    inProgress = "\'In Progress\'"

    query = \
        """
        UPDATE public.{}
        SET {} = {}
        WHERE {} = {} AND {} = {} 
        """.format(order_table_name, order_status_col, inProgress, order_listing_id_col, str(listingID), \
                   order_client_id_col, str(clientID))

    cur = conn.cursor()

    try:
        cur.execute(query)
        conn.commit()
        return "SUCCESS"
    # except Exception as e:
    #     raise Exception(e)
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()

    # return "SUCCESS"


# --------------------------------------------------- SEARCH ---------------------------------------------------#


@app.route('/api/search/<string:search_query>', methods=['GET'])
def search(search_query):
    """
    Return a string representation of a list of JSON objects. This list contains
    objects that correspond to listings that match names or tags in the search query.
    """
    # separate words in search_query with '+' in place of spaces
    search_terms = search_query.split('+')

    # want to remove whitespace and empty elements from the list
    search_terms_filtered = []

    for search_term in search_terms:
        if not search_term.isspace() and not search_term == '':
            search_terms_filtered.append(search_term)

    matched_rows_by_name = get_rows_from_name(search_terms_filtered)

    matched_rows_by_tag = get_rows_from_tag(search_terms_filtered)

    matched_rows = matched_rows_by_name + matched_rows_by_tag

    unique_matched_rows = list(set(matched_rows))  # remove duplicate rows

    rows_to_json(unique_matched_rows)  # want to convert each row into a JSON string

    return json.dumps({'data': unique_matched_rows})  # convert to string before returning


def get_rows_from_name(search_terms):
    """
    Return a list of listing tuples whose Food Names correspond to words in search_terms.
    """
    try:
        matched_rows = []

        for search_term in search_terms:
            search_names = conn.cursor()
            search_names.execute("SELECT t1.{}, t1.{}, t1.{}, t1.{},"
                                 " t1.{}, t1.{}, t1.{} FROM public.{} as t1"
                                 " FULL OUTER JOIN public.{} as t2 ON t1.{} = t2.{} "
                                 "WHERE UPPER(t1.{}) LIKE UPPER(\'%{}%\')".format(listing_listing_id_col,
                                                                                  listing_cook_id_col,
                                                                                  listing_food_name_col,
                                                                                  listing_price_col,
                                                                                  listing_location_col,
                                                                                  listing_image_col,
                                                                                  listing_active_col,
                                                                                  listing_table_name,
                                                                                  listing_tags_table_name,
                                                                                  listing_listing_id_col,
                                                                                  listing_tags_listing_id_col,
                                                                                  listing_food_name_col,
                                                                                  search_term))

            search_names_row = search_names.fetchone()

            while search_names_row is not None:
                matched_rows.append(search_names_row)
                search_names_row = search_names.fetchone()

            search_names.close()

        return matched_rows
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()


def get_rows_from_tag(search_terms):
    """
    Return a list of listing tuples whose tags correspond to words in search_terms.
    """
    try:
        matched_rows = []

        for search_term in search_terms:
            search_tags = conn.cursor()
            search_tags.execute("SELECT t1.{}, t1.{}, t1.{}, t1.{},"
                                " t1.{}, t1.{} FROM public.{} as t1"
                                " FULL OUTER JOIN public.{} as t2 ON t1.{} = t2.{} "
                                "WHERE UPPER(t2.{}) LIKE UPPER(\'%{}%\')".format(listing_listing_id_col,
                                                                                 listing_cook_id_col,
                                                                                 listing_food_name_col,
                                                                                 listing_price_col,
                                                                                 listing_location_col,
                                                                                 listing_image_col,
                                                                                 listing_table_name,
                                                                                 listing_tags_table_name,
                                                                                 listing_listing_id_col,
                                                                                 listing_tags_listing_id_col,
                                                                                 listing_tags_tag_col,
                                                                                 search_term))

            search_tags_row = search_tags.fetchone()

            while search_tags_row is not None:
                matched_rows.append(search_tags_row)
                search_tags_row = search_tags.fetchone()

            search_tags.close()

        return matched_rows
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()


def rows_to_json(rows):
    """
    Mutate rows such that each tuple in rows is converted to a JSON string representing the same information.
    """
    for i in range(len(rows)):
        rows[i] = json.dumps({'ListingID': rows[i][0],
                              'CookID': rows[i][1],
                              'Food Name': rows[i][2],
                              'Price': rows[i][3],
                              'Location': rows[i][4],
                              'Image': rows[i][5],
                             'status':rows[i][6]})


# --------------------------------------------------- MAKE ORDER ---------------------------------------------------#
@app.route('/api/addOrder/', methods=['POST'])
def add_order_req():
    if add_new_order(request.get_json()) == "Success":
        conn.commit()
        return "Success"
    conn.commit()
    return "Failed"

    return "Success"

def getQuantity(list_id, client_id):
    """ Returns an unused listing_id """
    cur = conn.cursor()
    sql = "SELECT {} FROM {} WHERE ({} = {}) AND ({} = {})".format("quantity",
                                                   order_table_name, order_listing_id_col, list_id, order_client_id_col, client_id)
    try:
        cur.execute(sql)
        curr_quantity = cur.fetchone()[0]
        print(curr_quantity)
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()
    return curr_quantity

def getClientTotalOrders(client_id):
    """ Returns an unused listing_id """
    cur = conn.cursor()
    sql = "SELECT {} FROM {} WHERE ({} = {}) AND ({} != '{}') AND ({} != '{}')".format("quantity",
                                                   order_table_name, order_client_id_col, client_id, order_status_col, "Canceled", order_status_col, "Completed")
    try:
        total_num_orders=0
        cur.execute(sql)
        all_quantities=[]
        single_row = cur.fetchone()
        while single_row is not None:
            all_quantities.append(single_row)
            single_row = cur.fetchone()

        for i in range(len(all_quantities)):
            print("adding quantity "+str(all_quantities[i][0]))
            total_num_orders+=all_quantities[i][0]

    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()
    return total_num_orders


def add_new_order(json_data):
    """
    Return a string representation of a list of JSON objects. This list contains
    objects that correspond to listings that match names or tags in the search query.
    """
    try:
        cur = conn.cursor()
        json_dict = json_data

        list_id = json_dict[removeQuotes(order_listing_id_col)]
        client_id = json_dict[removeQuotes(order_client_id_col)]
        time = json_dict[removeQuotes(order_time_of_order_col)]
        total_num_orders=getClientTotalOrders(client_id)
        if total_num_orders < 3:
            sql = "SELECT * FROM {} WHERE ({} = {}) AND ({} = {}) AND ({} != '{}') AND ({} != '{}')".format(order_table_name,
                                                           order_listing_id_col, list_id, order_client_id_col, client_id, order_status_col, "Canceled", order_status_col, "Completed")
            cur.execute(sql)
            fetched=cur.fetchone()
            print(fetched)
            if (fetched is None):
                status = "Pending"
                print("add new")
                sql = "INSERT INTO " + order_table_name + " VALUES (%s, %s, %s, %s, %s)"
                cur.execute(sql, (client_id, list_id, status, time, "1"))

            else:
                print("update existing")
                num = int(getQuantity(list_id, client_id))+1
                sql = \
                    """
                        UPDATE public.{}
                        SET {} = {}
                        WHERE {} = {} 
                    """.format(order_table_name, "quantity", str(num), order_client_id_col, str(client_id))
                cur.execute(sql)
            return "Success"
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()
    return "Failed"


def update_num_orders():
    """
    update number of orders a cook has received. Send updated response back to UI to display correct number of orders
    :return: Success or failure
    """

    cur = conn.cursor()
    # update the number of orders here - i.e. get quantity from listing table and ++


# -------------------------------------------------- GET ALL ORDERS ---------------------------------------------------#

@app.route("/api/getAllOrders/<int:clientID>", methods=['GET'])
def getAllOrders(clientID):
    try:
        all_orders = []

        search_all = conn.cursor()

        search_all.execute(
            "SELECT * FROM {} WHERE ({} = {}) AND ({} != '{}') AND ({} != '{}')".format(order_table_name, order_client_id_col,
                                                                       str(clientID), order_status_col, "Completed",order_status_col,"Canceled"))

        single_row = search_all.fetchone()

        while single_row is not None:
            all_orders.append(single_row)
            single_row = search_all.fetchone()

        search_all.close()

        orders_to_json(all_orders)  # want to convert each row into a JSON string

        return json.dumps({'data': all_orders})  # convert to string before returning
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()


def get_food_data(listing_Id):
    try:
        cur = conn.cursor()
        sql = "SELECT {}, {} FROM {} WHERE {} = {}".format(listing_food_name_col, listing_location_col,
                                                           listing_table_name, listing_listing_id_col,
                                                           listing_Id)

        cur.execute(sql)
        return cur.fetchone()
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()


def orders_to_json(rows):
    """
    Mutate rows such that each tuple in rows is converted to a JSON string representing the same information.
    """
    for i in range(len(rows)):
        extra_data = get_food_data(rows[i][1])
        rows[i] = json.dumps({'ClientID': rows[i][0],
                              'ListingID': rows[i][1],
                              'Status': rows[i][2],
                              'Food Name': extra_data[0],
                              'Location': extra_data[1]})


# -------------------------------------------------- CHECK HISTORY ----------------------------------------------------#


@app.route("/api/checkHistory/<int:clientID>", methods=['GET'])
def checkHistory(clientID):
    """
        Return a string representation of a list of JSON objects. This list contains
        objects that correspond to the order history of client id ClientID.
        @param clientID: the client id number.
        @rtype: str
    """

    cur = conn.cursor()
    query = "SELECT * FROM {} WHERE ({} = {}) AND ({} = '{}')".format(order_table_name, order_client_id_col,
                                                                       str(clientID), order_status_col, "Completed")

    try:
        cur.execute(query)
        status = cur.fetchall()
        convert_to_json(status)
        return json.dumps({'data': status})
    # except Exception as e:
    #     raise Exception(e)
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()

    # status = cur.fetchall()
    # convert_to_json(status)
    # return json.dumps({'data': status})


# --------------------------------------------------- LOGIN ---------------------------------------------------#
@app.route('/api/login/<string:userID>/<string:password>', methods=['GET'])
def login(userID, password):
    """ Returns userID if <userID, password> is a valid combination. """

    query = \
        """
        SELECT *
        FROM public.{}
        WHERE {} = {} AND {} = '{}'
        """.format(user_table_name, user_user_id_col, str(userID), user_password_col, str(password))

    cur = conn.cursor()

    try:
        cur.execute(query)
        result = cur.fetchall()
        if len(result) != 1:
            return "FAILED"
        else:
            return result[0][2].rstrip() + "," + result[0][3]
    # except Exception as e:
    #     raise Exception(e)
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()


# --------------------------------------------------- ADD COOK REVIEW ---------------------------------------------------#

@app.route('/api/addReview', methods=['POST'])
def addReview():
    """ Adds a review to the cook rating table """
    

    try:
        addToDBReview(request.get_json())
        conn.commit()
        return "Success"
    # except Exception as e:
    #     raise Exception(e)
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()
 
def addToDBReview(json_data):
    cur = conn.cursor()
    json_dict = json_data

    cook_id = json_dict[removeQuotes(cook_ratings_cook_id_col)]
    reviewer_id = json_dict[removeQuotes(cook_ratings_reviewer_id_col)]
    comments = json_dict[removeQuotes(cook_ratings_comments_col)]
    rating = json_dict[removeQuotes(cook_ratings_rating_col)]
    
    sql = "INSERT INTO " + cook_ratings_table_name + " VALUES (%s, %s, %s, %s)"
    try:
        cur.execute(sql, (cook_id, reviewer_id, comments, rating))
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()


def convert_to_json(rows):
    """
        Mutate rows such that each tuple in rows is converted to a JSON string representing the same information.
    """
    for i in range(len(rows)):
        rows[i] = json.dumps({'Food Name': rows[i][0],
                              'CookID': rows[i][1],
                              'Price': rows[i][2],
                              'Location': rows[i][3]})
                              
                              
# --------------------------------------------------- GET COOK REVIEWS ---------------------------------------------------#

"""
Gets cook review data like average rating
"""
@app.route('/api/cookAvgRating/<int:cookID>', methods=["GET"])
def cookAvgRating(cookID):
    info = {}
    cur = conn.cursor();
    sql = "SELECT {}, AVG({})  FROM public.{} WHERE {} = (%s) GROUP BY {}".format(cook_ratings_cook_id_col, 
    cook_ratings_rating_col, cook_ratings_table_name, 
    cook_ratings_cook_id_col, cook_ratings_cook_id_col )
    try:
        poyo = str(cookID)
        cur.execute(sql, (poyo,))
        avgtuple = cur.fetchone();
        if avgtuple != None:
            return str(avgtuple[1])
        else:
            return str(0)
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()
    return "failure"

"""
  Gets all reviews along with names and user ids of reviewers
"""  
@app.route('/api/cookReviews/<int:cookID>', methods=["GET"])
def cookGetReviews(cookID):
    info = {}
    cur = conn.cursor();
    sql = ("SELECT {},{}, {}, {}, {}, {} "
    "FROM public.{}, public.{} WHERE {} = {} AND {} = (%s)").format(cook_ratings_cook_id_col,
                                                                   cook_ratings_reviewer_id_col,
                                                                   cook_ratings_rating_col,
                                                                   cook_ratings_comments_col,
                                                                   user_fname_col,
                                                                   user_lname_col,
                                                                   cook_ratings_table_name,
                                                                   user_table_name,
                                                                   user_user_id_col,
                                                                   cook_ratings_reviewer_id_col,
                                                                   cook_ratings_cook_id_col)
    
    try:
        poyo = str(cookID)
        cur.execute(sql, (poyo,))
        
        jsonlst = []
        if cur.rowcount > 0:
            avgtuple = cur.fetchone();
            while avgtuple != None:
                jsonlst.append({
                "CookID": avgtuple[0],
                "ReviewerID": avgtuple[1],
                "Rating": avgtuple[2],
                "Comments": avgtuple[3],
                "FName": avgtuple[4],
                "LName": avgtuple[5]
                })
                avgtuple = cur.fetchone()
            return json.dumps(jsonlst)
        else:
            return str("none available")
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()
    return "failure"

    
      

# --------------------------------------------------- CLOSE LISTING ---------------------------------------------------#
"""
TODO: NEED API FOR FOLLOWING CONDITION - CUSTOMER CANNOT MAKE ORDER IF STATUS IN LISTING TABLE IS INACTIVE (i.e. THE
CHEF IS NO LONGER TAKING NEW ORDER REQUESTS FOR HIS/HER DISH. CHANGE DB ENTRIES IN BACKEND, REMOVE THE LISTING IN UI
"""
false = "\'false\'"

@app.route('/api/closeListing/<int:cookID>',methods=['GET'])
def closeListing(cookID):
    """ A function that closes a cook's listing.
        Returns "Success" on a sucessful change of the listing id's order to complete.
        @param cookID: close this cookID's listing.
        @rtype: str
    """
    query = \
        """
        UPDATE public.{}
        SET {} = {}
        WHERE {} = {}
        """.format(listing_table_name, listing_active_col, false, listing_cook_id_col, str(cookID))

    cur = conn.cursor()
    try:
        cur.execute(query)
        conn.commit()
        if cur.rowcount == 0:  # do we put this here?
            raise Exception(
                "The status of listing id's order was not changed. ClientID or ListingID may be out of range.")
        return "Success"
    except:
        rollback = conn.cursor()
        rollback.execute("ROLLBACK")
        rollback.commit()
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
    # host="0.0.0.0", port=80
