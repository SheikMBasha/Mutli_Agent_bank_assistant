common steps:
Optional to create venv: python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate

API:
To run API in terminal1, enter
uvicorn mock_api:app --host 0.0.0.0 --port 8085 --reload

test agent:
python .\main.py