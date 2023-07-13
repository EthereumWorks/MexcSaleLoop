import requests
import hashlib
import hmac
import time

# !!!!!! Укажите свои реальные значения ключа API и секретного ключа
api_key = 'APY_KEY' 
api_secret = 'APY_SECRET'

def get_account_balance(asset):
    # Формируем URL запроса для получения баланса аккаунта
    url = 'https://api.mexc.com/api/v3/account'
    # Формируем timestamp и подпись запроса
    timestamp = str(int(time.time() * 1000))
    params = f'timestamp={timestamp}'
    signature = hmac.new(api_secret.encode(), params.encode(), hashlib.sha256).hexdigest()

    # Отправляем GET-запрос к API
    response = requests.get(url, headers={'X-MEXC-APIKEY': api_key}, params={'timestamp': timestamp, 'signature': signature})

    # Проверяем статус-код ответа
    if response.status_code == 200:
        data = response.json()
        if 'balances' in data:
            for balance in data['balances']:
                if balance['asset'] == asset:
                    return float(balance['free'])
            print(f'Error: Balance for {asset} not found')
        else:
            print('Error: Failed to fetch balances')
    else:
        print(f'Error occurred while fetching account balance: {response.text}')

    return None

def place_order(symbol, side, type, quantity, current_price):
    # Формируем timestamp и подпись запроса
    timestamp = str(int(time.time() * 1000))

    # Формируем подпись запроса
    query_string = f'symbol={symbol}&side={side}&type={type}&quantity={quantity}&price={current_price}&timestamp={timestamp}'
    signature = hmac.new(api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    
    # Формируем данные запроса
    data = {
        'symbol': symbol,
        'side': side,
        'type': type,
        'quantity': quantity,
        'price': current_price,
        'timestamp': timestamp,
        'signature': signature
    }
    
    # Выполняем POST-запрос для продажи ETH по текущей рыночной цене
    response = requests.post('https://api.mexc.com/api/v3/order', headers={'X-MEXC-APIKEY': api_key}, data=data)

    # Обрабатываем ответ
    if response.status_code == 200:
        order_info = response.json()
        print('ETH successfully sold:')
        print(f'  Symbol: {order_info["symbol"]}')
        print(f'  Order ID: {order_info["orderId"]}')
        print(f'  Price: {order_info["price"]}')
        print(f'  Original Quantity: {order_info["origQty"]}')
        print(f'  Type: {order_info["type"]}')
        print(f'  Side: {order_info["side"]}')
        print(f'  Transact Time: {order_info["transactTime"]}')
        print()
    else:
        print(f'Error occurred during ETH sale: {response.text}')


# !!!!! Установите актив - NEON
asset = 'BNB'

# Получите баланс аккаунта
balance = get_account_balance(asset)
if balance is not None:
    print(f'Balance of {asset}: {balance}')

# Бесконечный цикл проверки баланса и размещения ордера

while True:
    # Получаем текущий баланс 
    balance = get_account_balance(asset)
    if balance is not None and balance > 0:

        # !!!!! Получаем текущую цену (заменить пару на пару с NEON)
        symbol = 'BNBUSDC'
        url = f'https://api.mexc.com/api/v3/ticker/bookTicker?symbol={symbol}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                # Если в ответе получен список цен для нескольких символов, находим нужную цену 
                for item in data:
                    if item['symbol'] == symbol:
                        price = float(item['bidPrice'])
                        print(price)
                        break
                else:
                    price = None
            elif isinstance(data, dict):
                # Если в ответе получена цена 
                price = float(data['bidPrice'])
            else:
                price = None
        else:
            price = None
        
        print(price)
        
        if price is not None:
            # Размещаем ордер по текущей цене на весь баланс ETH
            place_order(symbol, 'SELL', 'LIMIT', balance, price)
        else:
            print('Error occurred while fetching current price')
    
    time.sleep(0.1)  # Задержка в секундах перед следующей проверкой и размещением ордера
