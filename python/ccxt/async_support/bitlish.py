# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange
from ccxt.base.errors import NotSupported


class bitlish (Exchange):

    def describe(self):
        return self.deep_extend(super(bitlish, self).describe(), {
            'id': 'bitlish',
            'name': 'Bitlish',
            'countries': ['GB', 'EU', 'RU'],
            'rateLimit': 1500,
            'version': 'v1',
            'has': {
                'CORS': False,
                'fetchTickers': True,
                'fetchOHLCV': True,
                'withdraw': True,
            },
            'timeframes': {
                '1h': 3600,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766275-dcfc6c30-5ed3-11e7-839d-00a846385d0b.jpg',
                'api': 'https://bitlish.com/api',
                'www': 'https://bitlish.com',
                'doc': 'https://bitlish.com/api',
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': False,
            },
            'fees': {
                'trading': {
                    'tierBased': False,
                    'percentage': True,
                    'taker': 0.3 / 100,  # anonymous 0.3%, verified 0.2%
                    'maker': 0,
                },
                'funding': {
                    'tierBased': False,
                    'percentage': False,
                    'withdraw': {
                        'BTC': 0.001,
                        'LTC': 0.001,
                        'DOGE': 0.001,
                        'ETH': 0.001,
                        'XMR': 0,
                        'ZEC': 0.001,
                        'DASH': 0.0001,
                        'EUR': 50,
                    },
                    'deposit': {
                        'BTC': 0,
                        'LTC': 0,
                        'DOGE': 0,
                        'ETH': 0,
                        'XMR': 0,
                        'ZEC': 0,
                        'DASH': 0,
                        'EUR': 0,
                    },
                },
            },
            'api': {
                'public': {
                    'get': [
                        'instruments',
                        'ohlcv',
                        'pairs',
                        'tickers',
                        'trades_depth',
                        'trades_history',
                    ],
                    'post': [
                        'instruments',
                        'ohlcv',
                        'pairs',
                        'tickers',
                        'trades_depth',
                        'trades_history',
                    ],
                },
                'private': {
                    'post': [
                        'accounts_operations',
                        'balance',
                        'cancel_trade',
                        'cancel_trades_by_ids',
                        'cancel_all_trades',
                        'create_bcode',
                        'create_template_wallet',
                        'create_trade',
                        'deposit',
                        'list_accounts_operations_from_ts',
                        'list_active_trades',
                        'list_bcodes',
                        'list_my_matches_from_ts',
                        'list_my_trades',
                        'list_my_trads_from_ts',
                        'list_payment_methods',
                        'list_payments',
                        'redeem_code',
                        'resign',
                        'signin',
                        'signout',
                        'trade_details',
                        'trade_options',
                        'withdraw',
                        'withdraw_by_id',
                    ],
                },
            },
            'commonCurrencies': {
                'DSH': 'DASH',
                'XDG': 'DOGE',
            },
        })

    async def fetch_markets(self, params={}):
        markets = await self.publicGetPairs()
        result = []
        keys = list(markets.keys())
        for p in range(0, len(keys)):
            market = markets[keys[p]]
            id = market['id']
            symbol = market['name']
            base, quote = symbol.split('/')
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'info': market,
            })
        return result

    def parse_ticker(self, ticker, market):
        timestamp = self.milliseconds()
        symbol = None
        if market:
            symbol = market['symbol']
        last = self.safe_float(ticker, 'last')
        return {
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'high': self.safe_float(ticker, 'max'),
            'low': self.safe_float(ticker, 'min'),
            'bid': self.safe_float(ticker, 'bid'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'ask'),
            'askVolume': None,
            'vwap': None,
            'open': self.safe_float(ticker, 'first'),
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': self.safe_float(ticker, 'prc') * 100,
            'average': None,
            'baseVolume': self.safe_float(ticker, 'sum'),
            'quoteVolume': None,
            'info': ticker,
        }

    async def fetch_tickers(self, symbols=None, params={}):
        await self.load_markets()
        tickers = await self.publicGetTickers(params)
        ids = list(tickers.keys())
        result = {}
        for i in range(0, len(ids)):
            id = ids[i]
            market = self.markets_by_id[id]
            symbol = market['symbol']
            ticker = tickers[id]
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        tickers = await self.publicGetTickers(params)
        ticker = tickers[market['id']]
        return self.parse_ticker(ticker, market)

    async def fetch_ohlcv(self, symbol, timeframe='1h', since=None, limit=None, params={}):
        await self.load_markets()
        # market = self.market(symbol)
        now = self.seconds()
        start = now - 86400 * 30  # last 30 days
        if since is not None:
            start = int(since / 1000)
        interval = [str(start), None]
        return await self.publicPostOhlcv(self.extend({
            'time_range': interval,
        }, params))

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        orderbook = await self.publicGetTradesDepth(self.extend({
            'pair_id': self.market_id(symbol),
        }, params))
        timestamp = None
        last = self.safe_integer(orderbook, 'last')
        if last:
            timestamp = int(last / 1000)
        return self.parse_order_book(orderbook, timestamp, 'bid', 'ask', 'price', 'volume')

    def parse_trade(self, trade, market=None):
        side = 'buy' if (trade['dir'] == 'bid') else 'sell'
        symbol = None
        if market:
            symbol = market['symbol']
        timestamp = int(trade['created'] / 1000)
        return {
            'id': None,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': None,
            'type': None,
            'side': side,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetTradesHistory(self.extend({
            'pair_id': market['id'],
        }, params))
        return self.parse_trades(response['list'], market, since, limit)

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privatePostBalance()
        result = {'info': response}
        currencies = list(response.keys())
        balance = {}
        for c in range(0, len(currencies)):
            currency = currencies[c]
            account = response[currency]
            currency = currency.upper()
            # issue  #4 bitlish names Dash as DSH, instead of DASH
            if currency == 'DSH':
                currency = 'DASH'
            if currency == 'XDG':
                currency = 'DOGE'
            balance[currency] = account
        currencies = list(self.currencies.keys())
        for i in range(0, len(currencies)):
            currency = currencies[i]
            account = self.account()
            if currency in balance:
                account['free'] = float(balance[currency]['funds'])
                account['used'] = float(balance[currency]['holded'])
                account['total'] = self.sum(account['free'], account['used'])
            result[currency] = account
        return self.parse_balance(result)

    def sign_in(self):
        return self.privatePostSignin({
            'login': self.login,
            'passwd': self.password,
        })

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        order = {
            'pair_id': self.market_id(symbol),
            'dir': 'bid' if (side == 'buy') else 'ask',
            'amount': amount,
        }
        if type == 'limit':
            order['price'] = price
        result = await self.privatePostCreateTrade(self.extend(order, params))
        return {
            'info': result,
            'id': result['id'],
        }

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        return await self.privatePostCancelTrade({'id': id})

    async def withdraw(self, code, amount, address, tag=None, params={}):
        self.check_address(address)
        await self.load_markets()
        currency = self.currency(code)
        if code != 'BTC':
            # they did not document other types...
            raise NotSupported(self.id + ' currently supports BTC withdrawals only, until they document other currencies...')
        response = await self.privatePostWithdraw(self.extend({
            'currency': currency.lower(),
            'amount': float(amount),
            'account': address,
            'payment_method': 'bitcoin',  # they did not document other types...
        }, params))
        return {
            'info': response,
            'id': response['message_id'],
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            if method == 'GET':
                if params:
                    url += '?' + self.urlencode(params)
            else:
                body = self.json(params)
                headers = {'Content-Type': 'application/json'}
        else:
            self.check_required_credentials()
            body = self.json(self.extend({'token': self.apiKey}, params))
            headers = {'Content-Type': 'application/json'}
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
