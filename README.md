# Road Monitoring Application

Structure:
- `ap`: Access point for the sensor
- `sta`: Station (sensor) that connects to `ap` and sends detected events via LoRa
- `model`: ML model for labeling events
- `model-lambda`: Code for deploying the model in AWS Lambda
- `dashboard`: Dashboard to show identified events

