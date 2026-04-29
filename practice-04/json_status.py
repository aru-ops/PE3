import json

# Load JSON data from file
with open(r"C:\Users\Aruka\Desktop\practice4\practice-04\sample-data.json", "r") as file:
    data = json.load(file)

# Print table header
print("Interface Status")
print("="*79)
print(f"{'DN':<50} {'Description':<20} {'Speed':<6} {'MTU':<6}")
print("-"*50, "-"*20, "-"*6, "-"*6)

# Iterate through the interfaces
for intf in data['imdata']:  # assuming JSON has key 'imdata'
    # Extract fields
    dn = intf['l1PhysIf']['attributes'].get('dn', '')
    desc = intf['l1PhysIf']['attributes'].get('descr', '')
    speed = intf['l1PhysIf']['attributes'].get('speed', '')
    mtu = intf['l1PhysIf']['attributes'].get('mtu', '')

    # Print formatted row
    print(f"{dn:<50} {desc:<20} {speed:<6} {mtu:<6}")
