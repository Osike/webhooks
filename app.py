from flask import Flask, request, jsonify
import logging

# Initialize Flask app
app = Flask(__name__)

# Set up basic logging so we can see events in our terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/webhooks/africastalking', methods=['POST'])
def africastalking_webhook():
    """
    Endpoint that handles incoming Africa's Talking SMS Delivery Reports.
    """
    # 1. Receive the request 
    # Africa's Talking sends delivery reports as form-urlencoded data (or sometimes JSON)
    # request.form catches form data; request.get_json(silent=True) catches JSON.
    data = request.form.to_dict() or request.get_json(silent=True) or {}
    
    # 2. Log the event type and a safe reference ID
    # For SMS delivery reports, Africa's Talking sends fields like 'id' (messageId), 'status', and 'phoneNumber'
    event_status = data.get('status', 'UNKNOWN')
    safe_reference_id = data.get('id', 'NO_ID_PROVIDED')
    
    logger.info(f"Received Africa's Talking event. Ref ID: {safe_reference_id}, Status: {event_status}")
    
    # 3. Save the event or put it in a queue for later processing
    # (For this basic tutorial, we simulate pushing it to a background queue or DB)
    enqueue_event_for_background_processing(data)
    
    # 4. Return 200 OK immediately
    # This tells Africa's Talking: "Message received successfully, you can stop retrying."
    return jsonify({"status": "success", "message": "Webhook received"}), 200


def enqueue_event_for_background_processing(payload):
    """
    Placeholder function representing step 4. 
    In production, you would push this payload to Redis, Celery, 
    an AWS SQS queue, or insert it into a database table.
    """
    logger.info(f"-> [QUEUE SIMULATION] Storing payload for safe offline processing...")
    # e.g., db.save(payload) or redis_queue.push(payload)
    pass


if __name__ == '__main__':
    # Run the application locally on port 5000
    app.run(port=5000, debug=True)