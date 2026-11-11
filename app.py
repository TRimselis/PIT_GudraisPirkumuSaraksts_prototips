import streamlit as st

st.set_page_config(page_title="Smart Shopping List", page_icon="🛒", layout="wide")

PRODUCTS = {
    "Milk": {"category": "Dairy", "price": 1.49},
    "Cheese": {"category": "Dairy", "price": 2.39},
    "Yogurt": {"category": "Dairy", "price": 0.89},
    "Chicken breast": {"category": "Meat", "price": 3.99},
    "Minced beef": {"category": "Meat", "price": 4.79},
    "Apples": {"category": "Fruit & vegetables", "price": 1.79},
    "Bananas": {"category": "Fruit & vegetables", "price": 1.29},
    "Tomatoes": {"category": "Fruit & vegetables", "price": 2.19},
    "Potatoes": {"category": "Fruit & vegetables", "price": 1.49},
    "Bread": {"category": "Bakery", "price": 1.19},
    "Croissants": {"category": "Bakery", "price": 2.49},
    "Pasta": {"category": "Dry goods", "price": 1.09},
    "Rice": {"category": "Dry goods", "price": 1.69},
    "Coffee": {"category": "Drinks", "price": 3.49},
    "Orange juice": {"category": "Drinks", "price": 1.89},
    "Water": {"category": "Drinks", "price": 0.59},
    "Dishwashing liquid": {"category": "Household", "price": 2.29},
    "Paper towels": {"category": "Household", "price": 2.99},
}

STORE_LAYOUTS = {
    "Rimi": {
        "Dairy": 1,
        "Meat": 2,
        "Fruit & vegetables": 3,
        "Bakery": 4,
        "Dry goods": 5,
        "Drinks": 6,
        "Household": 7,
        "Other": 8,
    },
    "Maxima": {
        "Fruit & vegetables": 1,
        "Bakery": 2,
        "Dairy": 3,
        "Dry goods": 4,
        "Meat": 5,
        "Drinks": 6,
        "Household": 7,
        "Other": 8,
    },
    "Lidl": {
        "Bakery": 1,
        "Fruit & vegetables": 2,
        "Dairy": 3,
        "Meat": 4,
        "Dry goods": 5,
        "Drinks": 6,
        "Household": 7,
        "Other": 8,
    },
}

if "shopping_items" not in st.session_state:
    st.session_state["shopping_items"] = []
if "custom_products" not in st.session_state:
    st.session_state["custom_products"] = {}

def catalogue():
    return {**PRODUCTS, **st.session_state["custom_products"]}

def add_item(name, quantity):
    data = catalogue()[name]
    existing = next(
        (x for x in st.session_state["shopping_items"] if x["name"] == name),
        None
    )
    if existing:
        existing["quantity"] += quantity
    else:
        st.session_state["shopping_items"].append({
            "name": name,
            "category": data["category"],
            "price": float(data["price"]),
            "quantity": quantity,
            "done": False,
        })

def money(value):
    return f"€{value:.2f}"

st.title("Smart Shopping List")
st.caption("Build your list, organise products by store aisle, and keep track of your estimated total.")
st.info(
    "Proof of concept: prices and aisle layouts are sample data have no correlation with real life "
    "They do not represent verified, live information from individual retailer branches."
)

selected_store = st.selectbox(
    "Choose a store",
    list(STORE_LAYOUTS.keys()),
    key="selected_store",
)
aisle_layout = STORE_LAYOUTS[selected_store]
st.caption(f"Shopping at: **{selected_store}** · Product order will follow this store's demo aisle layout.")

left, right = st.columns([1, 1.5], gap="large")

with left:
    st.subheader("Add products")
    product_names = sorted(catalogue().keys())
    selected = st.selectbox("Choose a product", product_names)
    quantity = st.number_input("Quantity", min_value=1, max_value=99, value=1, step=1)
    if st.button("＋ Add to list", type="primary", use_container_width=True):
        add_item(selected, int(quantity))
        st.success(f"Added {quantity} × {selected}")

    with st.expander("Add a custom product"):
        custom_name = st.text_input("Product name")
        custom_category = st.selectbox(
            "Category",
            ["Dairy", "Meat", "Fruit & vegetables", "Bakery", "Dry goods", "Drinks", "Household", "Other"],
        )
        custom_price = st.number_input(
            "Estimated unit price (€)", min_value=0.0, value=1.0, step=0.1
        )
        if st.button("Add custom product", use_container_width=True):
            cleaned_name = custom_name.strip()
            if cleaned_name:
                st.session_state["custom_products"][cleaned_name] = {
                    "category": custom_category,
                    "price": float(custom_price),
                }
                add_item(cleaned_name, 1)
                st.success(f"Added {cleaned_name}")
            else:
                st.warning("Please enter a product name.")

with right:
    st.subheader("Your shopping list")
    if not st.session_state["shopping_items"]:
        st.write("Your list is empty. Add a product to get started.")
    else:
        view = st.radio("View", ["Smart aisle order", "Original list"], horizontal=True)

        def aisle_for(item):
            return aisle_layout.get(item["category"], aisle_layout["Other"])

        if view == "Smart aisle order":
            display_items = sorted(
                st.session_state["shopping_items"],
                key=lambda x: (aisle_for(x), x["name"].lower())
            )
        else:
            display_items = st.session_state["shopping_items"][:]

        for item in display_items:
            idx = st.session_state["shopping_items"].index(item)
            checkbox_key = f"done_{idx}"

            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = item["done"]

            c1, c2, c3, c4 = st.columns([0.10, 0.48, 0.18, 0.24])
            with c1:
                st.checkbox("Done", key=checkbox_key, label_visibility="collapsed")
                item["done"] = st.session_state[checkbox_key]

            with c2:
                if item["done"]:
                    st.markdown(f"~~{item['name']}~~")
                else:
                    st.markdown(f"**{item['name']}**")
                st.caption(
                    f"{item['category']} · Aisle {aisle_for(item)}"
                )

            with c3:
                st.caption(f"Qty: {item['quantity']}")

            with c4:
                st.write(money(item["price"] * item["quantity"]))
                if st.button("Remove", key=f"remove_{idx}"):
                    st.session_state["shopping_items"].pop(idx)
                    st.session_state.pop(checkbox_key, None)
                    st.rerun()

        total = sum(x["price"] * x["quantity"] for x in st.session_state["shopping_items"])
        total_products = sum(x["quantity"] for x in st.session_state["shopping_items"])
        completed_products = sum(
            x["quantity"] for x in st.session_state["shopping_items"] if x["done"]
        )
        remaining_total = sum(
            x["price"] * x["quantity"]
            for x in st.session_state["shopping_items"]
            if not x["done"]
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("Estimated total", money(total))
        m2.metric("Products", total_products)
        m3.metric("Completed", f"{completed_products}/{total_products}")

        progress = completed_products / total_products if total_products else 0
        st.progress(progress, text=f"Shopping progress: {progress:.0%}")

        st.divider()
        st.write(f"**Remaining estimate:** {money(remaining_total)}")

        if st.button("Clear completed items"):
            for i in range(len(st.session_state["shopping_items"])):
                st.session_state.pop(f"done_{i}", None)
            st.session_state["shopping_items"] = [
                x for x in st.session_state["shopping_items"] if not x["done"]
            ]
            st.rerun()

        if st.button("Clear entire list"):
            for i in range(len(st.session_state["shopping_items"])):
                st.session_state.pop(f"done_{i}", None)
            st.session_state["shopping_items"] = []
            st.rerun()

st.divider()
st.subheader("Store aisle layout")
st.write(f"Current demo layout for **{selected_store}**:")
layout_rows = sorted(aisle_layout.items(), key=lambda pair: pair[1])
st.table([{"Aisle": aisle, "Category": category} for category, aisle in layout_rows])

