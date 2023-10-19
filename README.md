# The Citizen Project Transit API

This project aims to allow Roosevelt Island residents to access transit times to and from the Island, and covers
the subway, tram and ferry. Although the API is specific to the island, you can clone the repository, and modify parameters
to extract train times for any of the subway stations within NYC.

## [Live Demo](https://d33owvrgueloug.cloudfront.net/)

## Getting Started

There are two ways you can get started. If you are considering to add/change code, follow instructions on Local Development. Otherwise, you
can get started with Docker.

1. Clone the repository
```bash
git clone https://github.com/TheCitizensProject/citizen-proj-transit.git
```

### Local Development

1. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```
1. Install the dependencies
```bash
pip install -r requirements.txt
```
1. Get an MTA API Key from [MTA Dev](https://new.mta.info/developers)

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

5. Run the Fast API app

```bash
uvicorn app:app --reload
```

### Docker

1. Make sure to have Docker installed in your system. If you are using a Mac, you can simply download [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Get an MTA API Key from [MTA Dev](https://new.mta.info/developers)

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

3. With Docker Desktop running in the background, run the following command:
   ```bash
   sudo docker compose build
   docker compose up -d
   ```

### Interacting with the API
Open your browser and paste the following endpoint:

#### Train
```
http://localhost:8000/api/get-station-time-unified/B06
```
This will return the train times for Roosevelt Island.
#### Ferry
```
http://localhost:8000/api/get-ferry-time
```
This will return the ferry times for Roosevelt Island.
#### Tram
```
http://localhost:8000/api/get-tram-time
```
This will return the tram times for Roosevelt Island.

You can also query `http://localhost:8000/docs` to access the FastAPI documentation and the interactive API.