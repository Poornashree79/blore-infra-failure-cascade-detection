import json
import xml.etree.ElementTree as ET
import os

def kml_to_geojson(kml_file, output_file, network_type):
    ns = {'k': 'http://www.opengis.net/kml/2.2'}
    tree = ET.parse(kml_file)
    root = tree.getroot()

    features = []
    point_id = 1
    line_id = 1

    for pm in root.findall('.//k:Placemark', ns):
        coords_el = pm.find('.//k:coordinates', ns)
        if coords_el is None:
            continue

        coords_text = coords_el.text.strip()
        coord_pairs = [c.split(',') for c in coords_text.split()]
        coords = [[float(c[0]), float(c[1])] for c in coord_pairs]

        if network_type == "water":
            if len(coords) == 1:
                properties = {
                    "id": f"wtp_{point_id:02d}",
                    "type": "water_treatment_plant",
                    "name": f"WTP {point_id}",
                    "operator": "BWSSB"
                }
                geometry = {"type": "Point", "coordinates": coords[0]}
                point_id += 1
            else:
                properties = {
                    "id": f"pipe_{line_id:02d}",
                    "type": "pipeline",
                    "material": "steel"
                }
                geometry = {"type": "LineString", "coordinates": coords}
                line_id += 1

        elif network_type == "power":
            if len(coords) == 1:
                properties = {
                    "id": f"sub_{point_id:02d}",
                    "type": "substation",
                    "voltage": "220kV",
                    "operator": "KPTCL"
                }
                geometry = {"type": "Point", "coordinates": coords[0]}
                point_id += 1
            else:
                properties = {
                    "id": f"line_{line_id:02d}",
                    "type": "transmission_line",
                    "voltage": "220kV"
                }
                geometry = {"type": "LineString", "coordinates": coords}
                line_id += 1

        elif network_type == "road":
            properties = {
                "id": f"road_{line_id:02d}",
                "name": f"Road {line_id}",
                "type": "highway",
                "class": "primary"
            }
            geometry = {"type": "LineString", "coordinates": coords}
            line_id += 1

        features.append({
            "type": "Feature",
            "properties": properties,
            "geometry": geometry
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_file, "w") as f:
        json.dump(geojson, f, indent=2)


# 🔥 AUTOMATIC PROCESSING FUNCTION
def process_all_kml():
    raw_folder = "data/raw"
    processed_folder = "data/processed"

    for file in os.listdir(raw_folder):
        if file.endswith(".kml"):
            input_path = os.path.join(raw_folder, file)

            # Decide type based on filename
            if "water" in file.lower():
                network_type = "water"
            elif "power" in file.lower():
                network_type = "power"
            elif "road" in file.lower():
                network_type = "road"
            else:
                print(f"Skipping {file} (unknown type)")
                continue

            output_file = file.replace(".kml", ".geojson")
            output_path = os.path.join(processed_folder, output_file)

            print(f"Processing {file} → {output_file}")
            kml_to_geojson(input_path, output_path, network_type)


# RUN THIS FILE
if __name__ == "__main__":
    process_all_kml()