#!/usr/bin/python3
# -*- coding: utf-8 -*-

from random import randint

# naivní opravdu všechny kombinace, rekurze
# heuristika podle, ceny, váhy, cena/váha
# naskládám předměty s nejvyšší cenou
# naskládám předměty s nejnižsí vahou
# naskládám předměty s nejlepším poměrěm vahou
# cena, váha, cena/váha


def generate_items(n, min_price, max_price, min_weight, max_weight):
	retval = []
	for i in range(n):
		data = {'id':i+1, 'price': randint(min_price, max_price), 'weight': randint(min_weight, max_weight)}
		data['ppw'] = data['price']/data['weight']
		retval.append(data)
	return retval

def main(args):
	items = generate_items(5, 1, 40, 1, 40)
	print(items)
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
