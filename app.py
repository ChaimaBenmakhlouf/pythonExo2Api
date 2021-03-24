
from functools import lru_cache
from flask import Flask, jsonify, request

# import overpass
# api = overpass.API()
import csv
import dns.resolver

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# def settings():
#     return 'settings'
@app.route("/")
def hello():
    return "hello world"

@lru_cache()
def parse_the_csv():
    with open(
        "short.csv", encoding="latin1"
    ) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        domains = {}
        registrars = {}
        for i, row in enumerate(reader):
            domains[row["Nom de domaine"]] = {
                "fqdn": row["Nom de domaine"],
                "registrar": f"/api/registrars/{row['Nom BE']}",
                "tld": row["Sous domaine"],
                
                               
                "owner": {
                    "type": row["Type du titulaire"],
                    "country": row["Pays titulaire"],
                    "department": row["Departement titulaire"],
                },
                "idn": row["Domaine IDN"],
                "created_at": row["Date de création"],
                "domain": f"/api/domains/{row['Nom de domaine']}",
                 
            }       

            registrars[row["Nom BE"]] = (
                {
                    "self": f"/api/registrars/{row['Nom BE']}",
                    "departement": row["Departement BE"],
                    "city": row["Ville BE"],
                    "name": row["Nom BE"],
                },
                )
        return domains, registrars       

         
@app.route("/api/domain/<fqdn>", methods=["GET"])
def api_root2(fqdn):
    response = {"items":[]}
    domains, registrars =  parse_the_csv()
    for name, row in domains.items():
        if row["fqdn"] == fqdn:
            response["items"].append(row)
    return response


@app.route("/api/domain/<fqdn>/dns/", methods=["GET", "PUT"])
def displayDNSInfo(fqdn):
    data = []    
    try:
        response = dns.resolver.query(fqdn, "MX")
        for rdata in response:
            
            data.append({
                "exchange": str(rdata.exchange),
                "preference": str(rdata.preference),
                "name": fqdn,
                "type": "MX"
            })
    except dns.resolver.NXDOMAIN:
        pass
    try:
        response2 = dns.resolver.query(fqdn, "A")
        for rdata in response2:
            data.append({
                "address": str(rdata.address),
                "name": fqdn,
                "type": "A"

        })
    except dns.resolver.NXDOMAIN:
        pass
    
    try:
        response3 = dns.resolver.query(fqdn, "TXT")
        for rdata in response3:
            data.append({
                "address": [txt.decode("UTF-8") for txt in rdata.strings],
                "name": fqdn,
                "type": "TXT"
            })
    except dns.resolver.NoAnswer:
        print(f'{fqdn}: No answer')
    except dns.resolver.NXDOMAIN:
        pass

    try:
        response4 = dns.resolver.query(fqdn, "NS")
        for rdata in response4:
            data.append({
                "address": str(rdata.target),
                "name": fqdn,
                "type": "NS"
            })
    except dns.resolver.NXDOMAIN:
        pass
    return {"entries": data,
            "fqdn": fqdn
    } 