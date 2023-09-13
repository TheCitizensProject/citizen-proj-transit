# The Citizen Project Transit API

This project aims to allow Roosevelt Island residents to access transit times to and from the Island, and covers
the subway, tram and ferry. Although the API is specific to the island, you can clone the repository, and modify parameters
to extract train times for any of the subway stations within NYC.

## [Live Demo](https://d33owvrgueloug.cloudfront.net/)

## Getting Started

1. Clone the repository
```bash
git clone https://github.com/farhan0167/citizen-proj-transit
```
2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install the dependencies
```bash
pip install -r requirements.txt
```
4. Get an MTA API Key from [MTA Dev](https://new.mta.info/developers)

Once you obtain the key, you need to create a `.env` file within the root directory.
```bash
nano .env
```
with the text editor open, paste the following:
```bash
MTA-KEY=your-mta-key
```
Press Control+X, and press Y when prompted to save.

Or you can just add a new file with the `.env` name, and paste the `MTA-KEY=your-mta-key`.

5. Run the Flask app

```bash
python3 app.py
```

6. Open your browser and paste the following endpoint:

```
https://localhost:8000/api/get-station-time/B06
```
This will return the train times for Roosevelt Island.