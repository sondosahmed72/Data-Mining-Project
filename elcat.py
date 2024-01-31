import pandas as pd
import itertools

deepest_itemsets = []


def read_data(file_path):
    df = pd.read_excel(file_path)

    if set(df.columns) == {"TID", "items"}:
        print("Horizontal format detected")
        print(df.head())
        vertical_data = {}
        for index, row in df.iterrows():
            items = str(row["items"]).split(",")
            for item in items:
                item = item.strip()
                vertical_data.setdefault(item, set()).add(row["TID"])
        print("Now printing vertical data")
        print(vertical_data)
        return vertical_data

    elif set(df.columns) == {"itemset", "TID_set"}:
        print("Vertical format detected")
        df["TID_set"] = df["TID_set"].apply(lambda x: set(map(str, x.split(","))))
        return df.groupby("itemset")["TID_set"].sum().to_dict()

    else:
        raise ValueError("Invalid or unknown data format")


def eclat(prefix, items, frequent_itemsets, min_support):
    for i, itids in sorted(items, key=lambda x: len(x[1]), reverse=True):
        new_prefix = prefix + [i]
        new_prefix_set = frozenset(new_prefix)
        frequent_itemsets[new_prefix_set] = len(itids)

        suffix_items = []
        for j, jtids in items:
            if j > i:
                common_tids = itids & jtids
                if len(common_tids) >= min_support:
                    suffix_items.append((j, common_tids))

        if suffix_items:
            eclat(new_prefix, suffix_items, frequent_itemsets, min_support)


def generate_frequent_itemsets(vertical_data, min_support):
    frequent_itemsets = {}
    eclat([], list(vertical_data.items()), frequent_itemsets, min_support)
    return frequent_itemsets


def generate_association_rules(frequent_itemsets, min_confidence, total_transactions):
    rules = []
    for itemset in frequent_itemsets.keys():
        if len(itemset) > 1:
            for i in range(1, len(itemset)):
                for antecedent in itertools.combinations(itemset, i):
                    antecedent = frozenset(antecedent)
                    consequent = itemset - antecedent
                    conf = frequent_itemsets[itemset] / frequent_itemsets[antecedent]
                    if conf >= min_confidence:
                        rule = (antecedent, consequent, conf)
                        lift = calculate_lift(
                            rule, frequent_itemsets, total_transactions
                        )
                        rules.append((antecedent, consequent, conf, lift))
    return rules


def calculate_lift(rule, frequent_itemsets, total_transactions):
    antecedent, consequent = rule[0], rule[1]
    support_A = frequent_itemsets[antecedent] / total_transactions
    support_B = frequent_itemsets[consequent] / total_transactions
    support_AB = frequent_itemsets[antecedent | consequent] / total_transactions
    lift = support_AB / (support_A * support_B)
    return lift


file_path = "C:\\Users\\sondo\\OneDrive\\Desktop\\Data Mining\\Horizontal_Format.xlsx"
data = read_data(file_path)
df1 = pd.read_excel(file_path)
total_transactions = len(df1)

min_support = 3#0.6 * total_transactions
min_confidence = 0.8

frequent_itemsets = generate_frequent_itemsets(data, min_support)
rules = generate_association_rules(
    frequent_itemsets, min_confidence, total_transactions
)
max_length = max(len(itemset) for itemset in frequent_itemsets.keys())

for rule in rules:
    antecedent, consequent, confidence, lift = rule
    print(
        f"Rule: {set(antecedent)} -> {set(consequent)}, "
        f"Confidence: {confidence:.2f}, Lift: {lift:.2f}"
    )

print("\nLongest Frequent Itemsets in Vertical Format:")
for itemset, count in frequent_itemsets.items():
    if len(itemset) == max_length:
        print(f"{itemset}: Transaction Count = {count}")
