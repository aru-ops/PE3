import re
import json

def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

def normalize_price(price_str):
    """Converts price like '1 200,00' -> 1200.00 (float)"""
    clean = price_str.replace(" ", "").replace(",", ".")
    return float(clean)

def extract_products_with_prices(text):
    """
    Extracts product name and its total cost (line before 'Стоимость')
    """
    # Match: product name, quantity x price, total, Стоимость
    pattern = re.compile(
        r'\d+\.\n(.+?)\n[\d\s,]+ x [\d\s,]+\n([\d\s,]+)\nСтоимость',
        re.MULTILINE
    )
    items = []
    for match in pattern.findall(text):
        name = match[0].strip()
        price = normalize_price(match[1].strip())
        items.append({"name": name, "price": price})
    return items

def extract_total(text):
    match = re.search(r'ИТОГО:\n([\d\s,]+)', text)
    return normalize_price(match.group(1)) if match else None

def extract_payment_method(text):
    match = re.search(r'(Банковская карта|Наличные)', text)
    return match.group(1) if match else None

def extract_datetime(text):
    match = re.search(r'Время:\s*([\d\.]+\s[\d:]+)', text)
    return match.group(1) if match else None

def parse_receipt(filename):
    text = read_file(filename)
    products = extract_products_with_prices(text)
    total_reported = extract_total(text)
    payment_method = extract_payment_method(text)
    datetime = extract_datetime(text)
    calculated_total = round(sum(item["price"] for item in products), 2)

    data = {
        "products": products,
        "reported_total": total_reported,
        "calculated_total": calculated_total,
        "payment_method": payment_method,
        "datetime": datetime
    }

    return data

if __name__ == "__main__":
    receipt_data = parse_receipt("raw.txt")
    print("\n===== PARSED RECEIPT =====\n")
    print(json.dumps(receipt_data, indent=4, ensure_ascii=False))