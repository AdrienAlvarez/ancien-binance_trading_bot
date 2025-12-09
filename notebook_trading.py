pip install python-binance
pip install schedule

import requests
import pandas as pd
import time
import math

#Connection à l'API binance pour trader via mon compte
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.exceptions import BinanceAPIException
client = Client(api_key, api_secret)

#Pour acheter ou revendre une quantité de crypto, il faut arrondir ce chiffre suivant les règles de binance
def round_down(quantity, symbol):
    info = client.get_symbol_info(symbol)
    step_size = [float(_['stepSize']) for _ in info['filters'] if _['filterType'] == 'LOT_SIZE'][0]
    step_size = '%.8f' % step_size
    step_size = step_size.rstrip('0')
    decimals = len(step_size.split('.')[1])
    return math.floor(quantity * 10 ** decimals) / 10 ** decimals

#Programme de trading crypto
def trade_crypto(x):
    
  #Import des traders avec leurs positions
  uid = "126603A7082B3D92896CCB5142DC8FE4"
  r = requests.post('https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition', json={"encryptedUid":uid,"tradeType":"PERPETUAL"})
  j = r.json()
  uid2 = "B2B7057819137AA5D328A44486DF335B"
  r2 = requests.post('https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition', json={"encryptedUid":uid2,"tradeType":"PERPETUAL"})
  j2 = r2.json()
  uid3 = "B57354EB2EC9D2E9C698E723659F339C"
  r3 = requests.post('https://www.binance.com/bapi/futures/v1/public/future/leaderboard/getOtherPosition', json={"encryptedUid":uid3,"tradeType":"PERPETUAL"})
  j3 = r3.json()
  df_positions = pd.DataFrame(j['data']['otherPositionRetList'])
  df_positions2 = pd.DataFrame(j2['data']['otherPositionRetList'])
  df_positions3 = pd.DataFrame(j3['data']['otherPositionRetList'])
  assemblage = pd.concat((df_positions,df_positions2,df_positions3))

  #filtrage des positions
  df_pnl = assemblage[assemblage["pnl"]>0.01]
  df_roe = df_pnl[df_pnl["roe"]>0.01]
  pnl_positif = df_roe[df_roe["entryPrice"]<df_roe["markPrice"]]
  df_scraping = pnl_positif.drop_duplicates("symbol").reset_index(drop=True)


  #Solde actuel pour acheter des crypto
  portefeuille_USDT = round(float(client.get_asset_balance(asset='USDT')['free']),2)

  #Affiche la crypto et son prix à l'unité
  price = client.get_symbol_ticker(symbol= x + "USDT")
  #Affiche seulement le prix à l'unité de cette crypto
  prix_crypto_unit_euro = float(price['price'])
  #Affiche le portefeuille de cette crypto
  portefeuille_crypto = float(client.get_asset_balance(asset=x )['free'])
  #Affiche le nombre de crypto à vendre (en cas de vente)
  vente_cryto = round_down(portefeuille_crypto, x + "USDT")
  #Affiche combien je peux acheter de cryptomonnaie avec "13€"
  quantity_crypto_treize = round_down(13/prix_crypto_unit_euro,x + "USDT")
  #Affiche le nombre de cryptomonnaie à acheter
  achat_quantity_crypto = round_down(quantity_crypto_treize, x + "USDT")
  #Affiche le chiffre qui détermine si le porte monnaie et vide ou plein
  portefeuille_vide = 13/prix_crypto_unit_euro/100

  #Si le df_scrap affiche une crypto & que le portefeuille est vide & que j'ai assez d'argent == j'achète cette crypto
  if df_scraping['symbol'].str.contains(x + "USDT").any() and portefeuille_crypto<portefeuille_vide and portefeuille_USDT>13:
    buy_order = client.create_order(symbol=x + "USDT", side='BUY', type='MARKET', quantity=quantity_crypto_treize)
    print("Félicitation, tu viens d'acheté " + str(quantity_crypto_treize) + " "+ x + "!")
  #Si le df_scrap affiche une crypto & que le portefeuille est vide & que je n'ai pas assez d'argent == je ne fais rien
  elif df_scraping['symbol'].str.contains(x + "USDT").any() and portefeuille_crypto<portefeuille_vide and portefeuille_USDT<13:
    print("Tu n'as malheureusement pas assez d'argent disponible pour acheter du " + x )
  #Si le df_scrap affiche une crypto & que le portefeuille est plein == je ne fais rien
  elif df_scraping['symbol'].str.contains(x + "USDT").any() and portefeuille_crypto>portefeuille_vide:
    print("Tu possède déjà " + str(portefeuille_crypto) + x)
  #Si le df_scrap n'affiche pas une crypto & que le portefeuille est vide == je ne fais rien
  elif ~df_scraping['symbol'].str.contains(x + "USDT").any() and portefeuille_crypto<=portefeuille_vide:
    print("La cryptomonnaie " + x + " n'apparait pas dans les positions à prendre pour le moment")
  #Si le df_scrap n'affiche pas une crypto & que le portefeuille est plein == je vend cette crypto
  elif ~df_scraping['symbol'].str.contains(x + "USDT").any() and portefeuille_crypto>portefeuille_vide:
    buy_order = client.create_order(symbol=x + "USDT", side='SELL', type='MARKET', quantity=vente_cryto)
    print("Félicitation, tu as vendu " + str(portefeuille_crypto) + " "+ x + "!")

while True:
  for i in ["FTT","LIT","DOGE","ETH","MANA"]:
          trade_crypto(i)
          time.sleep(2.5)
