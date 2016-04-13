#!/usr/bin/python
# -*- coding: utf-8 -*-

import btcchina
import json
import time
import sys



print '\n'
###############################################
flag = 0
flagBalance = 0
flagOrders = 0

gap = 30

step =5
tradeAmount = 1


if len(sys.argv) == 2:
	if sys.argv[1] == "init":
		print 'initialize all'
		flagBalance = 1
		flagOrders = 1

################################################

f = open('time','r')
OLDtime = f.readline()
f.close()

OLDmyBTC = 0.
OLDmyCNY = 0.
f=open('balance','r')
lines = f.readlines()
f.close()
OLDmyBTC = float(lines[0].strip())
OLDmyCNY = float(lines[1].strip())

OLDbuyOrders = []
f=open('buy','r')
lines = f.readlines()
f.close()
for line in lines:
	strs = line.strip().split()
	temp = [float(strs[0]),float(strs[1]),float(strs[2]),int(strs[3])]
	OLDbuyOrders.append(temp)

OLDsellOrders = []
f=open('sell','r')
lines = f.readlines()
f.close()
for line in lines:
	strs = line.strip().split()
	temp = [float(strs[0]),float(strs[1]),float(strs[2]),int(strs[3])]
	OLDsellOrders.append(temp)



#############################################
access_key="YOUR-ACCESS-KEY"
secret_key="YOUR-SECRET-KEY"

bc = btcchina.BTCChina(access_key,secret_key)

''' These methods have no arguments '''
accountInfo = bc.get_account_info()
myBTC = round(float(accountInfo["balance"]["btc"]["amount"])) + round(float(accountInfo["frozen"]["btc"]["amount"]))
myCNY = round(float(accountInfo["balance"]["cny"]["amount"])) + round(float(accountInfo["frozen"]["cny"]["amount"]))

#print json.dumps(accountInfo,indent=4, separators=(',', ': '))
#result = bc.get_market_depth2()
#print result

# NOTE: for all methods shown here, the transaction ID could be set by doing
#result = bc.get_account_info(post_data={'id':'stuff'})
#print result


''' cancel requires id number of order '''
#result = bc.cancel(2)
#print result

''' request withdrawal requires currency and amount '''
#result = bc.request_withdrawal('BTC',0.1)
#print result

''' get deposits requires currency. the optional "pending" defaults to true '''
#result = bc.get_deposits('BTC',pending=False)
#print result

''' get orders returns status for one order if ID is specified,
    otherwise returns all orders, the optional "open_only" defaults to true '''
#result = bc.get_orders(2)
#print result
#print json.dumps(myOrders["order"],indent=4, separators=(',', ': '))

myBuyOrders = []
mySellOrders = []
getOrders = bc.get_orders(open_only=True)
for order in getOrders["order"]:
	temp = [float(order["price"]), float(order["amount"]), float(order["amount_original"]), order["id"]]
	if order["type"] == "bid":
		myBuyOrders.append(temp)
	elif order["type"] == "ask":
		mySellOrders.append(temp)
	else:
		print "ERROR: strange order type!!!"
		exit(0)
myBuyOrders.sort(reverse = True)
mySellOrders.sort(reverse = True)


def NewOrders(diff):
	print 'create',diff,'new oders!'
	if mySellOrders != OLDsellOrders:
		print "sell orders:"
		for i in OLDsellOrders:
			if i not in mySellOrders:
				print i[0],'filled, need to create a new buy order:',i[0]-gap
				''' buy and sell require price (CNY, 5 decimals) and amount (LTC/BTC, 8 decimals) '''
				result = bc.buy(i[0]-gap,tradeAmount)
				print 'Order created: id',result,'\n'

	if myBuyOrders != OLDbuyOrders:
		print "buy orders:"
		for i in OLDbuyOrders:
			if i not in myBuyOrders:
				print i[0],'filled, need to create a new sell order:',i[0]+gap
				''' buy and sell require price (CNY, 5 decimals) and amount (LTC/BTC, 8 decimals) '''
				result = bc.sell(i[0]+gap,tradeAmount)
				print 'Order created: id',result,'\n'


if flagBalance == 0:
	if myBTC != OLDmyBTC or myCNY != OLDmyCNY:
		print "Balance changed:"
		print "my BTC:\n",OLDmyBTC,'--->',myBTC
		print "my CNY:\n",OLDmyCNY,'--->',myCNY
		if abs(myBTC - OLDmyBTC) > 10 or abs(myCNY - OLDmyCNY) > 30000: 
			print 'wrong!'
			exit(1)
	else:
		print 'No change in Balance!'
		flagBalance = 1
print '\n'

if flagOrders == 0:
	diff = len(OLDsellOrders)+len(OLDbuyOrders) - ( len(mySellOrders)+len(myBuyOrders) )
	if diff != 0:
		if 0 < diff < 5:
			NewOrders(diff)
		elif diff >= 5:
			print 'order changes too much!!!!!!!!\n'
			print 'old:'
			print OLDbuyOrders,'\n',OLDsellOrders
			print "############################"
			print 'now:'
			print myBuyOrders,'\n',mySellOrders
		else:
			pass
	else:
		print 'No change in Orders!'
		flagOrders = 1

if flagOrders == 1:
#if flagBalance == 1 and flagOrders == 1:
	flag = 1

if flag == 1:
	f = open('balance','w')
	f.write( str(myBTC)+ '\n'+ str(myCNY)+ '\n')
	f.close()

	print 'sell orders begin from:'
	f = open('sell','w')
	for t in range(len(mySellOrders)):
		i = mySellOrders[t]
		j = mySellOrders[t-1]
		if j[0] - i[0] != step:
			print i[0]
		else:
			#print '...'
			pass

		strs = str(i[0])+' '+str(i[1])+' '+str(i[2])+' '+str(i[3])
		f.write(strs+'\n')
	f.close()
	print 'end at:\n',i[0]

	print 'buy oders begin from:'
	f = open('buy','w')
	for t in range(len(myBuyOrders)):
		i = myBuyOrders[t]
		j = myBuyOrders[t-1]
		if j[0] - i[0] != step:
			print i[0]
		else:
			print '...'
		strs = str(i[0])+' '+str(i[1])+' '+str(i[2])+' '+str(i[3])
		f.write(strs+'\n')
	f.close()
	print 'end at:\n',i[0]
	
	print '\ntotal order number:',len(myBuyOrders)+len(mySellOrders)
	localtime = time.asctime( time.localtime(time.time()) )
	f = open('time','w')
	f.write(localtime+'\n')
	f.close()
	print "\norders checked, no change since:","\n++++++++++++++++++\n",OLDtime,"++++++++++++++++++\n"

''' get withdrawals returns status for one transaction if ID is specified,
    if currency is specified it returns all transactions,
    the optional "pending" defaults to true '''
#result = bc.get_withdrawals(2)
#print result
#result = bc.get_withdrawals('BTC',pending=True)
#print result
 
''' Fetch transactions by type. Default is 'all'. 
    Available types 'all | fundbtc | withdrawbtc | fundmoney | withdrawmoney | 
    refundmoney | buybtc | sellbtc | tradefee'
    Limit the number of transactions, default value is 10 '''
#result = bc.get_transactions('all',10)
#print result

'''get archived order returns a specified id order which is archived,
   the market default to "BTCCNY" and the "withdetail" default to false,if "withdetail" is specified to "true", the result will include the order's detail'''
#result = bc.get_archived_order(2,'btccny',False)
#print result

'''get archived orders returns the orders which order id is less than the specified "less_than_order_id",and the returned amount is defined in "limit",
   default value is 200, if "withdetail" is specified to "true",
   the result will include to orders' detail'''
#result = bc.get_archived_orders('btccny',200,10000,False)
#print result
