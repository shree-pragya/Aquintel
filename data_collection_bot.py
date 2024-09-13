# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# import tensorflow as tf
import json
# from sklearn.metrics import accuracy_score, precision_score, recall_score
# from sklearn.model_selection import train_test_split
# from tensorflow.keras import layers, losses, saving
# from tensorflow.keras.datasets import fashion_mnist
# from tensorflow.keras.models import Model, load_model
# from datetime import datetime
import websockets
# import pymongo

import pymongo
import asyncio
import ssl
import certifi

ca = certifi.where()

myclient = pymongo.MongoClient("mongodb+srv://aquintel66:j7RTuWouBsjzyRqF@cluster0.arwxp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", tlsCAFile=ca)

mydb = myclient["mydatabase"]
static_dataset = mydb["test_static"]
position_dataset = mydb["test_position"]

# print(myclient.server_info())

async def connect_ais_stream():
  async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {"APIKey": "<API_KEY>",  # Required !
                            #  "BoundingBoxes": [[[23.625663463280404, 66.31232119844522], [15.899274547801024, 74.17853223505227]]], # Required!
                            #  "BoundingBoxes": [[[24.95942098751467, 59.454508068184865], [13.8937972985918, 76.34879308712635]]], # Required!
                            #  "BoundingBoxes": [[[22.71234, 67.81223], [22.71141, 73.83124]], [[16.03114, 67.81142], [22.71123, 73.83123]]], # Required!
                             "BoundingBoxes": [[[28.85898853164005, -96.78569202255129],[24.12156459876252, -82.81108247148403]]], # Required!
                            #  "FiltersShipMMSI": ["368207620", "367719770", "211476060"], # Optional!
                             "FilterMessageTypes": ["PositionReport", "ShipStaticData"] # Optional!
        }

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        async for message_json in websocket:
            message = json.loads(message_json)

            message_type = message["MessageType"]

            print(message_type, message['MetaData']['MMSI'])

            if message_type == "ShipStaticData":
                
                ais_message_static = message['Message']['ShipStaticData']
                
                static_data = static_dataset.find_one_and_update({"mmsi":ais_message_static['MetaData']['MMSI']},
                                            { '$set':{"draught":ais_message_static['MaximumStaticDraught'],
                                            "type":ais_message_static['Type'],
                                            "dimension":ais_message_static['Dimension'],
                                            "eta":ais_message_static['eta']}}
                                            )
                
                if not static_data:
                    static_dataset.insert_one({"mmsi":ais_message_static['MetaData']['MMSI'],
                                        "draught":ais_message_static['MaximumStaticDraught'],
                                        "type":ais_message_static['Type'],
                                        "dimension":ais_message_static['Dimension'],
                                        "eta":ais_message_static['eta']
                                        })
                
                print("static data entered")
                
            elif message_type == "PositionReport":
                
                static_data = static_dataset.find_one({"mmsi":message['MetaData']['MMSI']})
                
                if static_data:
                
                    ais_message = message['Message']['PositionReport']
                # data_arr = np.array([[ais_message['Latitude'],
                #                      ais_message['Longitude'],
                #                      ais_message['Sog'],
                #                      ais_message['Cog'],
                #                      ais_message['TrueHeading'],
                #                     #  ais_message_static['MaximumStaticDraught'],
                #                     #  ais_message_static['Type'],
                #                     #  max(ais_message_static['Dimension']['A'], ais_message_static['Dimension']['B']),
                #                     #  max(ais_message_static['Dimension']['C'],ais_message_static['Dimension']['D']),
                #                     #     ais_message_static['eta']
                #                      ]])

                # data_arr = (data_arr - min_val) / (max_val - min_val)

                # print(accuracy(data_arr))

                    position_dataset.insert_one({"mmsi":message['MetaData']['MMSI'], 
                                        "Latitude":ais_message['Latitude'], 
                                        "Longitude":ais_message['Longitude'], 
                                        "Sog":ais_message['Sog'],
                                        "Cog":ais_message['Cog'],
                                        "Heading":ais_message['TrueHeading']
                                        })
                    
                    print("position data entered")
            # print("done")
                
                
if __name__ == '__main__':
    asyncio.run(asyncio.run(connect_ais_stream()))