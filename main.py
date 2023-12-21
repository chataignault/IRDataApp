from fastapi import FastAPI
import json
from json import JSONEncoder
from typing import Optional
from pydantic import BaseModel

import os
import pandas as pd
import numpy as np

from analytics.analytics import *

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:8000/ir_analysis"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/item/{item_id}")
async def get_item(item_id:int): # data parsing and data validation
    return {"item": item_id}

@app.get("/json/{json_data}&{key}")
async def read_json(json_data, key):
    data = json.loads(json_data)
    # do something with data
    return json.dumps(data[key])

@app.post("/items/")
async def create_item(item: Item):
    # item_dict = item.dict() 
    return item

@app.post("/items/{item_id}")
async def create_item_with_ID(item_id:int, item: Item):
    # item_dict = item.dict() 
    return {item_id: item}

def get_dataframe():
    return pd.DataFrame(
        {
            "nom":["Robert", "Gertrude"]
        }
    )

@app.get("/data/example")
def read_df():
    return get_dataframe().to_dict()

@app.get("/data/{file_name}")
def read_csv(file_name:str):
    data = pd.read_csv(os.path.join(os.getcwd(), file_name)).set_index("Prenom")
    print(data)
    print(data.to_dict())
    return data.to_dict()

# @app.get("/ir_data/{file_name}")
# def read_ir_data(file_name:str):
#     path = os.path.join(r"C:\Users\leonc\leon\Cours\Cours3A\FI\PCA on Treasury Bonds", "^"+file_name+".csv")
#     data = pd.read_csv(path)
#     return data.to_json(orient="records")

@app.get("/ir_data/{file_name}")
def read_ir_data_cropped(file_name:str, n_rows:int=10):
    path = os.path.join(r"C:\Users\leonc\leon\Cours\Cours3A\FI\PCA on Treasury Bonds", data_dir,  "^"+file_name+".csv")
    data = pd.read_csv(path)
    return data.iloc[:n_rows].to_json(orient="records")


########################################################################


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

@app.get("/ir_analysis/")
def process_PCA():
    rates = load_rates_from_dict(data_dir, treasury_bonds)
    _, D, V = get_principal_components(rates.values)
    return json.dumps({"array": V}, cls=NumpyArrayEncoder)