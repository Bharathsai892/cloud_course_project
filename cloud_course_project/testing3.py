import xml.etree.ElementTree as ET

def parse_traces(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    traces = {}

    # Extract vehicle ID and their routes
    for vehicle in root.findall('vehicle'):
        vid = vehicle.get('id')
        route_element = vehicle.find('route')  # Find the <route> element inside <vehicle>
        
        if route_element is not None:
            route = route_element.get('edges')  # Get the 'edges' attribute from <route>
            if route:
                traces[vid] = route.split()  # Split the edges into a list
            else:
                print(f"Warning: No edges found for vehicle {vid}")
        else:
            print(f"Warning: No route element found for vehicle {vid}")
    
    return traces

if __name__ == "__main__":
    # Call the function with the actual file path of your .trips.xml file
    traces = parse_traces('trips.trips(1).xml')  # Replace with your actual file path
    
    # Print the extracted traces
    for vid, route in traces.items():
        print(f"Vehicle {vid}: {route}")
