# Tito webhook server
import mysql.connector, hmac, hashlib, base64
from flask import Flask, request, abort

app = Flask(__name__)

# This is reversed proxied by nginx, this is NOT the public address
# This is the interal address localhost:5000/hacknotts2023 in this case
@app.route('/hacknotts2023', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        with open("./secrets/sqlserver_pass", "r") as file:
            sql_pass = file.read().strip()

        with open("./secrets/sqlserver_user", "r") as file:
            sql_user = file.read().strip()

        try:
            db = mysql.connector.connect(
            host="localhost",
            user=sql_user,
            password=sql_pass,
            database="HackNotts"
            )
            db_cursor = db.cursor()
        except mysql.connector.DatabaseError:
            print("UNABLE TO CONNECT TO DATABASE")

        # Did it send json?
        if request.is_json:
            data = request.json
        else:
            abort(404)

        with open("./secrets/tito_key", "r") as file:
            tito_key = file.read().strip()

        # Verify the payload
        tito_key = tito_key.encode()
        hash = hashlib.sha256
        expected = base64.b64encode(hmac.new(tito_key, request.data, hash).digest()).strip()

        try:
            verified = hmac.compare_digest(expected, request.headers['Tito-Signature'].encode())
        except KeyError:
            abort(404)

        if verified:
            if data['_type'] == 'ticket':
                ticket_ref = data['reference']      # Ticket reference
                ticket_type = data['release_title'] # Ticket type attendee/volunteer/sponsor

                if data['state_name'] == 'void': # If the ticket is voided then remove from database
                    sql = "DELETE FROM `People` WHERE `TicketRef` = %s"
                    db_cursor.execute(sql, (ticket_ref,))
                    db.commit()

                else:
                    try:
                        discord_tag = data['responses']['what-is-your-discord-tag']
                    except KeyError:
                        discord_tag = None

                    if discord_tag is None:
                        sql = "INSERT INTO `People` (`TicketRef`, `TicketType`) VALUES (%s, %s)"
                        values = (ticket_ref, ticket_type)
                    else:
                        sql = "INSERT INTO `People` (`DiscordTag`, `TicketRef`, `TicketType`) VALUES (%s, %s, %s)"
                        values = (discord_tag, ticket_ref, ticket_type)

                    try:
                        db_cursor.execute(sql, values)
                        db.commit()
                    except mysql.connector.errors.IntegrityError: # Ticket has been transfered or tag updated
                        try:
                            if discord_tag is None:
                                sql = "UPDATE `People` SET `DiscordTag` = %s WHERE `TicketRef` = %s"
                                values = (None, ticket_ref)
                            else:
                                # Update discord tag
                                sql = "UPDATE `People` SET `DiscordTag` = %s WHERE `TicketRef` = %s"
                                values = (discord_tag, ticket_ref)
                            db_cursor.execute(sql, values)
                            db.commit()
                        except mysql.connector.errors.IntegrityError:
                            pass # Not a lot can be done ngl

            return 'success', 200
        else:
            abort(404)
    else:
        abort(404)

if __name__ == '__main__':
    app.run()