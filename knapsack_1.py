#!/usr/bin/python3
# -*- coding: utf-8 -*-

import click
from pprint import pprint
import time


def load_instances(instances_file, solutions_file):
	instances = {}
	#~ ins = open(instances_file, 'r')
	with open(instances_file, 'r') as ins:
		for line in ins:
			data = line.split(' ')
			ins_size = int(data[1])
			instances[int(data[0])] = {
				'size': ins_size,
				'capacity': int(data[2]),
				'weights': list(map(int, data[3::2])),
				'prices': list(map(int, data[4::2])),
			}
	#~ ins.close()

	#~ sol = open(solutions_file, 'r')
	with open(solutions_file, 'r') as sol:
		for line in sol:
			data = line.split(' ')
			ins_id = int(data[0])
			instances[ins_id]['opt_sol'] = {
				'price': int(data[2]),
				'items': list(map(bool, map(int, data[4:]))),
			}
	#~ sol.close()
	return instances

def bf_rec2(instance, depth, price, weight, items):
	if depth < instance['size']:
		items[depth] = True
		price += instance['prices'][depth]
		weight += instance['weights'][depth]
		if price > instance['bf_sol']['price'] and weight <= instance['capacity']:
			instance['bf_sol']['price'] = price
			instance['bf_sol']['weight'] = weight
			instance['bf_sol']['items'] = items[:]
		bf_rec(instance, depth+1, price, weight, items)

		items[depth] = False
		price -= instance['prices'][depth]
		weight -= instance['weights'][depth]
		bf_rec(instance, depth+1, price, weight, items)

def bfc_rec(instance, depth, price, weight, items, rest_items):
	if weight > instance['capacity']:
		return

	if price > instance['bfc_sol']['price'] and weight <= instance['capacity']:
		instance['bfc_sol']['price'] = price
		instance['bfc_sol']['weight'] = weight
		instance['bfc_sol']['items'] = items[:]

	if depth < instance['size']:
		if price+rest_items[depth] < instance['bfc_sol']['price']:
			return
		items[depth] = True
		bfc_rec(
			instance, depth+1, price+instance['prices'][depth], weight+instance['weights'][depth], items, rest_items
		)
		items[depth] = False
		bfc_rec(instance, depth+1, price, weight, items, rest_items)

def brute_force_cut(instance, ins_id):
	tmp_instance = instance.copy()
	heur_ppw(tmp_instance, ins_id)
	instance['bfc_sol'] = {
		'price': tmp_instance['hppw_sol']['price'],
		'weight': tmp_instance['hppw_sol']['weight'],
		'items': tmp_instance['hppw_sol']['items']
	}
	items = [False for i in range(instance['size'])]
	rest_items = instance['prices'][:]
	for i in range(instance['size']-1, 0, -1):
		rest_items[i-1]+=rest_items[i]
	bfc_rec(instance=instance, depth=0, price=0, weight=0, items=items, rest_items=rest_items)
	if instance['bfc_sol']['price'] != instance['opt_sol']['price']:
		print('FAAAAAAAIL opt: {}, bfc: {}'.format(instance['opt_sol']['price'], instance['bfc_sol']['price']))

def bf_rec1(instance, depth, price, weight, items):
	if price > instance['bf_sol']['price'] and weight <= instance['capacity']:
		instance['bf_sol']['price'] = price
		instance['bf_sol']['weight'] = weight
		instance['bf_sol']['items'] = items[:]

	if depth < instance['size']:
		items[depth] = True
		bf_rec(instance, depth+1, price+instance['prices'][depth], weight+instance['weights'][depth], items)
		items[depth] = False
		bf_rec(instance, depth+1, price, weight, items)

def bf_rec(instance, depth, price, weight, items):
	if depth < instance['size']:
		items[depth] = True
		bf_rec(instance, depth+1, price+instance['prices'][depth], weight+instance['weights'][depth], items)
		items[depth] = False
		bf_rec(instance, depth+1, price, weight, items)
	elif price > instance['bf_sol']['price'] and weight <= instance['capacity']:
		instance['bf_sol']['price'] = price
		instance['bf_sol']['weight'] = weight
		instance['bf_sol']['items'] = items[:]

def brute_force(instance, ins_id):
	instance['bf_sol'] = {
		'price': 0,
		'weight': 0,
		'items': [False for i in range(instance['size'])]
	}
	items = [False for i in range(instance['size'])]
	bf_rec(instance=instance, depth=0, price=0, weight=0, items=items)

def heur_ppw(instance, ins_id):
	data = [(i, instance['prices'][i]/instance['weights'][i]) for i in range(instance['size'])]
	data.sort(key=lambda item: item[1], reverse=True)
	items = [False for i in range(instance['size'])]
	weight = 0
	price = 0
	for item in data:
		if weight + instance['weights'][item[0]] < instance['capacity']:
			weight += instance['weights'][item[0]]
			price += instance['prices'][item[0]]
			items[item[0]] = True
	instance['hppw_sol'] = {
		'price': price,
		'weight': weight,
		'items': items
	}

def heur_price(instance, ins_id):
	data = [(i, instance['prices'][i]) for i in range(instance['size'])]
	data.sort(key=lambda item: item[1], reverse=True)
	items = [False for i in range(instance['size'])]
	weight = 0
	price = 0
	for item in data:
		if weight + instance['weights'][item[0]] < instance['capacity']:
			weight += instance['weights'][item[0]]
			price += item[1]
			items[item[0]] = True
	instance['hpri_sol'] = {
		'price': price,
		'weight': weight,
		'items': items
	}

def heur_weight(instance, ins_id):
	data = [(i, instance['weights'][i]) for i in range(instance['size'])]
	data.sort(key = lambda item: item[1])
	items = [False for i in range(instance['size'])]
	weight = 0
	price = 0
	for item in data:
		if weight + item[1] < instance['capacity']:
			weight += item[1]
			price += instance['prices'][item[0]]
			items[item[0]] = True
	instance['hwei_sol'] = {
		'price': price,
		'weight': weight,
		'items': items
	}

def print_sol(sol, id_sol, opt_price, time=None):
	print(
		'{};{};{};{};{:.04f};'.format(id_sol, len(sol['items']), sol['price'], sol['weight'], sol['price']/opt_price),
		end=''
	)
	if time:
		print('{:.04f};'.format(time),end='')
	for item in sol['items']:
		print('{};'.format(item),end='')
	print()

@click.command()
@click.option(
	'--instances-file', '-i',
	type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True),
	help='path to file with instances', prompt='Enter path to file with instances'
)
@click.option(
	'--solutions-file', '-s',
	type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True),
	help='path to file with solutions', prompt='Enter path to file with solutions'
)
@click.option(
	'--repeats', '-r', default=1, type=click.IntRange(1, 1000),
	help='number of retition of each instance'
)
@click.option('--time-measure', '-t', default=True, type=click.BOOL, help='display time per insance')
@click.option(
	'--algorithm', '-a', prompt='Select algorithm', 
	type=click.Choice(['hw', 'hp', 'hppw', 'bf', 'bfc']), help='algorithm type'
)
def main(instances_file, solutions_file, time_measure, repeats, algorithm):
	instances = load_instances(instances_file, solutions_file)
	index = 1

	sol_to_print = 'opt_sol'
	if algorithm == 'bf':
		sol_to_print = 'bf_sol'
	elif algorithm == 'bfc':
		sol_to_print = 'bfc_sol'
	elif algorithm == 'hw':
		sol_to_print = 'hwei_sol'
	elif algorithm == 'hp':
		sol_to_print = 'hpri_sol'
	elif algorithm == 'hppw':
		sol_to_print = 'hppw_sol'

	for key, instance in instances.items():
		if time_measure:
			start = time.time() 
		for i in range(repeats):
			if algorithm == 'bf':
				brute_force(instance, key)
			elif algorithm == 'bfc':
				brute_force_cut(instance, key)
			elif algorithm == 'hw':
				heur_weight(instance, key)
			elif algorithm == 'hp':
				heur_price(instance, key)
			elif algorithm == 'hppw':
				heur_ppw(instance, key)

		if time:
			#~ print('time: {:0.3f}s'.format((time.time() - start)/repeats), end='')
			print_sol(instance[sol_to_print], key, instance['opt_sol']['price'], (time.time() - start)/repeats)
		else:
			print_sol(instance[sol_to_print], key, instance['opt_sol']['price'])
		index += 1
	#~ pprint(instances)
	return 0


if __name__ == '__main__':
	main()
