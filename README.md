# Medicine Stock & Expiry Tracker

A small beginner-friendly Streamlit app for tracking medicines, batches, expiry dates and stock movements. It is an educational local app, not a clinical or pharmacy operations system.

## Run locally

1. Open a terminal in this folder.
2. Create and activate a virtual environment:

   ```text
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install Streamlit:

   ```text
   pip install -r requirements.txt
   ```

4. Start the app:

   ```text
   streamlit run app.py
   ```

Data is stored in `data/medicines.json`, `data/batches.json`, and `data/movements.json`. Missing files start as empty lists. Invalid JSON is reported instead of being overwritten.

## Deploy the app

This is a Streamlit app, so deploy it with **Streamlit Community Cloud** or another host that can run a persistent Python process. Vercel's Python runtime expects a serverless `app`, `application`, or `handler` function and cannot run Streamlit directly. If Vercel reports `PYTHON_ENTRYPOINT_NOT_FOUND` for `app.py`, use Streamlit Community Cloud instead:

1. Push this repository to GitHub.
2. Open [share.streamlit.io](https://share.streamlit.io).
3. Choose this repository and the `main` branch.
4. Set the main file to `app.py`.

The local JSON files are suitable for this educational single-user project. A hosted multi-user app would need persistent shared storage.

## Run tests

```text
python -m unittest discover -s tests
```

## Main rules

- A batch is expired only when its expiry date is before today.
- A batch expiring today or within 90 days is near expiry.
- Expired stock is excluded from usable stock.
- Stock-out must be positive, cannot exceed the batch quantity, and cannot use an expired batch.
