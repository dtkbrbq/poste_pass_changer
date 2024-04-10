import requests
import os
from flask import Flask, request
import re
import secrets
from flask_basicauth import BasicAuth

api_username = os.environ.get("api_username")
api_pass = os.environ.get("api_pass")
tg_token = os.environ.get('tg_bot_token')
chat_id = os.environ.get('chat_id')
api_auth_pass = os.environ.get('api_auth_pass')
change_name = os.environ.get('change_name')

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = api_username
app.config['BASIC_AUTH_PASSWORD'] = api_auth_pass

basic_auth = BasicAuth(app)

@app.route('/api', methods=['POST'])
@basic_auth.required
def get_data():
  mailbox = re.search(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', str(request.data))
  mailserver = re.search(r'@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', str(request.data))
  responce, new_pass = pass_change(mailbox = mailbox.group(0), mailserver = mailserver.group(0).replace("@",""))
  if responce == 204:
    if tg_token != None:
      send_text = "https://api.telegram.org/bot"+tg_token+"/sendMessage?chat_id="+chat_id+"&parse_mode=Markdown&text="+f'Пароль от {mailbox.group(0)} изменен на {new_pass}'
      r = requests.get(send_text)
      r.json()
    return 'ok', 200
  else:
    return 'Password change failed', 500

def pass_change(mailbox, mailserver):
  new_pass = secrets.token_urlsafe(16)
  session = requests.Session()
  session.auth = (f'{api_username}@{mailserver}', api_pass)
  auth = session.post(f'https://mail.{mailserver}/admin/api/v1/boxes/')
  if change_name == "True":
    r = session.patch(f'https://mail.{mailserver}/admin/api/v1/boxes/{mailbox}', json = {"passwordPlaintext": f'{new_pass}', "name": f'{new_pass}'})
  else:
    r = session.patch(f'https://mail.{mailserver}/admin/api/v1/boxes/{mailbox}', json = {"passwordPlaintext": f'{new_pass}'})
  result = r.status_code
  return result, new_pass

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
