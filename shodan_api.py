from flask import Flask
from flask import request
from dig_shodan import dig_shodan
app = Flask("app")

@app.route("/")
def hello(methods=['GET']):
    ip = request.args.get('ip')
    if len(ip) > 15:
        return "{}"
    dig = dig_shodan("./chromedriver")
    dig.set_ip(str(ip))
    dig.crawl_web()
    dig.show_json()
    json_api = dig.return_json()
    return json_api

if __name__ == "__main__":
    app.run()