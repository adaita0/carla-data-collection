import json





def json_to_sentence(json_line):
    data = json.loads(json_line)
    frame = data.get("frame")
    timestamp = data.get("timestamp")

    output = f"Frame {frame} at time {timestamp:.2f} seconds: "

    if "image_path" in data:
        output += f"Captured image at '{data['image_path']}'. "
    if "accelerometer" in data:
        acc = data["accelerometer"]
        output += f"Accelerometer reading - x: {acc['x']:.2f}, y: {acc['y']:.2f}, z: {acc['z']:.2f}. "
    if "gyroscope" in data:
        gyro = data["gyroscope"]
        output += f"Gyroscope reading - x: {gyro['x']:.2e}, y: {gyro['y']:.2e}, z: {gyro['z']:.2e}. "
    if "compass" in data:
        output += f"Compass reading: {data['compass']:.2f} radians. "
    if "detections" in data:
        detections = data["detections"]
        output += f"{len(detections)} detections: "
        for i, det in enumerate(detections[:3]):  # limit to first 3 detections for brevity
            output += (f"[{i+1}] depth: {det['depth']:.2f}m, azimuth: {det['azimuth']:.2f}, "
                       f"altitude: {det['altitude']:.2f}, velocity: {det['velocity']:.2f}. ")
        if len(detections) > 3:
            output += f"...and {len(detections) - 3} more."

    return output.strip()



def main():
    input_file = 'data.jsonl'  # Ensure this matches your actual filename
    print("reached")
    try:
        with open(input_file, 'r') as f:
            print("reached")
            for line in f:
                try:
                    print("reached")
                    print(json_to_sentence(line))
                    
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON line: {e}")
    except Exception as e:
        print(f"Error reading file: {e}")