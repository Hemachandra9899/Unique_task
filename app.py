from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///baggage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class BagScan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bag_tag_id = db.Column(db.String(100), nullable=False)
    destination_gate = db.Column(db.String(10), nullable=False)
    location_scanned = db.Column(db.String(100), nullable=False)
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/baggage/scan', methods=['POST'])
def scan_bag():
    data = request.get_json()
    scan = BagScan(
        bag_tag_id=data['bag_tag_id'],
        destination_gate=data['destination_gate'],
        location_scanned=data['location_scanned']
    )
    db.session.add(scan)
    db.session.commit()
    return jsonify({"scan_internal_id": scan.id, "status": "logged"})

@app.route('/baggage/scans/bag/<bag_tag_id>')
def get_bag_scans(bag_tag_id):
    scans = BagScan.query.filter_by(bag_tag_id=bag_tag_id).order_by(BagScan.scanned_at.desc()).all()
    if request.args.get('latest') == 'true':
        return jsonify(scans[0].__dict__) if scans else ('', 404)
    return jsonify([scan.__dict__ for scan in scans])

@app.route('/baggage/scans/gate/<destination_gate>')
def get_gate_scans(destination_gate):
    scans = BagScan.query.filter_by(destination_gate=destination_gate).order_by(BagScan.scanned_at.desc()).all()
    return jsonify([scan.__dict__ for scan in scans])

@app.route('/baggage/active/gate/<destination_gate>')
def get_active_bags(destination_gate):
    minutes = int(request.args.get('since_minutes', 60))
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    scans = BagScan.query.filter(BagScan.destination_gate==destination_gate, BagScan.scanned_at >= cutoff).order_by(BagScan.scanned_at.desc()).all()

    seen = {}
    for scan in scans:
        if scan.bag_tag_id not in seen:
            seen[scan.bag_tag_id] = {
                "bag_tag_id": scan.bag_tag_id,
                "last_scan_at": scan.scanned_at,
                "last_location": scan.location_scanned
            }
    return jsonify(list(seen.values()))

@app.route('/baggage/stats/gate-counts')
def count_bags_per_gate():
    minutes = int(request.args.get('since_minutes', 60))
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    scans = BagScan.query.filter(BagScan.scanned_at >= cutoff).all()

    gate_map = {}
    for scan in scans:
        gate_map.setdefault(scan.destination_gate, set()).add(scan.bag_tag_id)

    return jsonify([{
        "destination_gate": gate,
        "unique_bag_count": len(tags)
    } for gate, tags in gate_map.items()])

if __name__ == '__main__':
    app.run(debug=True)
