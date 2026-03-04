import re
import json


def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def normalize_price(price_str):
    """
    Converts price like '1 200,00' -> 1200.00 (float)
    """
    clean = price_str.replace(" ", "").replace(",", ".")
    return float(clean)


def extract_prices(text):
    # Matches prices like: 308,00 or 1 200,00
    pattern = r'\d{1,3}(?:\s\d{3})*,\d{2}'
    return re.findall(pattern, text)


def extract_products(text):
    """
    Extract product blocks:
    Number.
    Product name
    Quantity x price
    Total
    """
    product_pattern = r'\d+\.\n(.+?)\n\d+,\d{3}\s*x\s*[\d\s,]+'
    return re.findall(product_pattern, text)


def extract_total(text):
    match = re.search(r'ИТОГО:\n([\d\s,]+)', text)
    return match.group(1) if match else None


def extract_payment_method(text):
    match = re.search(r'(Банковская карта|Наличные)', text)
    return match.group(1) if match else None


def extract_datetime(text):
    match = re.search(r'Время:\s*([\d\.]+\s[\d:]+)', text)
    return match.group(1) if match else None


def calculate_total_from_items(text):
    """
    Extract item totals (lines before word 'Стоимость')
    """
    totals_pattern = r'\n([\d\s]+,\d{2})\nСтоимость'
    totals = re.findall(totals_pattern, text)

    total_sum = sum(normalize_price(t) for t in totals)
    return round(total_sum, 2)


def parse_receipt(filename):
    text = read_file(filename)

    prices = extract_prices(text)
    products = extract_products(text)
    total_reported = extract_total(text)
    payment_method = extract_payment_method(text)
    datetime = extract_datetime(text)
    calculated_total = calculate_total_from_items(text)

    data = {
        "products": products,
        "all_prices_found": prices,
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