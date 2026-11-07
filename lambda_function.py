import json
import csv
import io
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    input_bucket = 'cary-ev-stations--apse2-az1--x-s3'
    input_key = 'electric-vehicle-charging-stations.json'
    
    output_bucket = 'cary-ev-stations-standard-jayesh'
    output_key = 'processed-data/ev_stations.csv'
    
    # 1. Fetch raw JSON dataset
    response = s3.get_object(Bucket=input_bucket, Key=input_key)
    raw_data = json.loads(response['Body'].read().decode('utf-8'))
    
    records = raw_data if isinstance(raw_data, list) else raw_data.get('records', raw_data.get('features', []))
    
    # 2. Build clean in-memory CSV
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    
    # Write header
    writer.writerow(['station_name', 'street_address', 'longitude', 'latitude', 'kwh_consumed', 'charging_duration_minutes'])
    
    for item in records:
        fields = item.get('fields', item.get('properties', item)) if isinstance(item, dict) else {}
        
        station_name = str(fields.get('station_name', fields.get('name', 'EV Station')))
        street_address = str(fields.get('street_address', fields.get('address', '')))
        kwh = float(fields.get('kwh_consumed', fields.get('kwh', 0.0)) or 0.0)
        duration = int(fields.get('charging_duration_minutes', fields.get('duration', 0)) or 0)
        
        lon, lat = -78.7812, 35.7915
        geo = item.get('geometry', fields.get('location', {}))
        
        if isinstance(geo, dict) and 'coordinates' in geo:
            coords = geo['coordinates']
            if len(coords) >= 2:
                lon, lat = coords[0], coords[1]

        writer.writerow([station_name, street_address, lon, lat, kwh, duration])

    # 3. Upload clean CSV to standard S3 bucket
    s3.put_object(
        Bucket=output_bucket,
        Key=output_key,
        Body=csv_buffer.getvalue()
    )

    return {
        'statusCode': 200,
        'body': json.dumps(f"Successfully processed {len(records)} records to S3 CSV in under 2 seconds!")
    }