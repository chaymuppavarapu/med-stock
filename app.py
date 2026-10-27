import streamlit as st

from alerts import expired_batches, low_stock_medicines, near_expiry_batches
from file_manager import load_records, save_records
from inventory import change_stock, expiry_status, make_batch, usable_stock
from medicine import find_medicine, make_medicine


MEDICINES_FILE = "medicines.json"
BATCHES_FILE = "batches.json"
MOVEMENTS_FILE = "movements.json"


def load_data() -> tuple[list[dict], list[dict], list[dict]]:
    return (
        load_records(MEDICINES_FILE),
        load_records(BATCHES_FILE),
        load_records(MOVEMENTS_FILE),
    )


def show_dashboard(medicines, batches):
    st.header("Dashboard")
    active = [medicine for medicine in medicines if medicine["is_active"]]
    expired = expired_batches(batches)
    near_expiry = near_expiry_batches(batches)
    low_stock = low_stock_medicines(medicines, batches)
    usable_total = sum(usable_stock(medicine["id"], batches) for medicine in medicines)
    columns = st.columns(5)
    columns[0].metric("Active medicines", len(active))
    columns[1].metric("Batches", len(batches))
    columns[2].metric("Usable units", usable_total)
    columns[3].metric("Expired batches", len(expired))
    columns[4].metric("Near expiry", len(near_expiry))
    st.subheader("Low-stock medicines")
    st.dataframe(
        [{"Medicine": medicine["name"], "Usable stock": usable_stock(medicine["id"], batches),
          "Reorder level": medicine["reorder_level"]} for medicine in low_stock],
        use_container_width=True,
    )


def show_medicines(medicines, batches):
    st.header("Medicine catalogue")
    search = st.text_input("Search by medicine name")
    visible = [medicine for medicine in medicines if search.lower() in medicine["name"].lower()]
    st.dataframe(visible, use_container_width=True)
    with st.form("medicine_form"):
        st.subheader("Add medicine")
        name = st.text_input("Name")
        category = st.text_input("Category")
        unit = st.text_input("Unit", value="tablets")
        reorder_level = st.number_input("Reorder level", min_value=0, step=1)
        if st.form_submit_button("Add medicine"):
            try:
                medicines.append(make_medicine(medicines, name, category, unit, reorder_level))
                save_records(MEDICINES_FILE, medicines)
                st.success("Medicine added.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))
    st.subheader("Activate or deactivate")
    for medicine in medicines:
        label = "Deactivate" if medicine["is_active"] else "Activate"
        if st.button(f"{label} {medicine['name']}", key=f"toggle_{medicine['id']}"):
            medicine["is_active"] = not medicine["is_active"]
            save_records(MEDICINES_FILE, medicines)
            st.rerun()


def show_batches(medicines, batches):
    st.header("Batch inventory")
    rows = []
    for batch in batches:
        medicine = find_medicine(medicines, batch["medicine_id"])
        rows.append({
            "Medicine": medicine["name"] if medicine else "Unknown",
            "Batch": batch["batch_number"],
            "Quantity": batch["quantity"],
            "Received": batch["received_date"],
            "Expiry": batch["expiry_date"],
            "Status": expiry_status(batch["quantity"], batch["expiry_date"]),
        })
    st.dataframe(rows, use_container_width=True)
    active = [medicine for medicine in medicines if medicine["is_active"]]
    if not active:
        st.info("Add an active medicine before creating a batch.")
        return
    with st.form("batch_form"):
        st.subheader("Add batch")
        selected = st.selectbox("Medicine", active, format_func=lambda item: item["name"])
        batch_number = st.text_input("Batch number")
        received_date = st.date_input("Received date")
        expiry_date = st.date_input("Expiry date")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        if st.form_submit_button("Add batch"):
            try:
                batches.append(make_batch(
                    batches, selected["id"], batch_number,
                    received_date.isoformat(), expiry_date.isoformat(), quantity,
                ))
                save_records(BATCHES_FILE, batches)
                st.success("Batch added.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))


def show_movements(medicines, batches, movements):
    st.header("Stock movement")
    if batches:
        with st.form("movement_form"):
            selected = st.selectbox("Batch", batches, format_func=lambda item: item["batch_number"])
            movement_type = st.selectbox("Type", ["IN", "OUT"])
            quantity = st.number_input("Quantity", min_value=1, step=1)
            reason = st.text_input("Reason")
            if st.form_submit_button("Save movement"):
                try:
                    change_stock(batches, movements, selected["id"], movement_type, quantity, reason)
                    save_records(BATCHES_FILE, batches)
                    save_records(MOVEMENTS_FILE, movements)
                    st.success("Movement saved.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
    st.subheader("Movement history")
    st.dataframe(movements, use_container_width=True)


def show_alerts(medicines, batches):
    st.header("Expiry alerts")
    medicine_names = {medicine["id"]: medicine["name"] for medicine in medicines}
    for title, items in [("Expired", expired_batches(batches)), ("Near expiry", near_expiry_batches(batches))]:
        st.subheader(title)
        st.dataframe([
            {"Medicine": medicine_names.get(item["medicine_id"], "Unknown"),
             "Batch": item["batch_number"], "Quantity": item["quantity"], "Expiry": item["expiry_date"]}
            for item in items
        ], use_container_width=True)
    st.subheader("Low stock")
    st.dataframe([{"Medicine": item["name"], "Usable stock": usable_stock(item["id"], batches),
                   "Reorder level": item["reorder_level"]}
                  for item in low_stock_medicines(medicines, batches)], use_container_width=True)


def main():
    st.set_page_config(page_title="Medicine Stock Tracker", layout="wide")
    try:
        medicines, batches, movements = load_data()
    except ValueError as error:
        st.error(str(error))
        st.stop()
    page = st.sidebar.radio("Go to", ["Dashboard", "Medicines", "Batches", "Movements", "Alerts"])
    if page == "Dashboard":
        show_dashboard(medicines, batches)
    elif page == "Medicines":
        show_medicines(medicines, batches)
    elif page == "Batches":
        show_batches(medicines, batches)
    elif page == "Movements":
        show_movements(medicines, batches, movements)
    else:
        show_alerts(medicines, batches)


if __name__ == "__main__":
    main()
