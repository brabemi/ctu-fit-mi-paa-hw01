#!/usr/bin/python3
# -*- coding: utf-8 -*-

import click
from pprint import pprint
import time


def load_instances(instances_file, solutions_file):
	instances = {}
	ins = open(instances_file, 'r')
	for line in ins:
		data = line.split(' ')
		ins_size = int(data[1])
		instances[int(data[0])] = {
			'size': ins_size,
			'capacity': int(data[2]),
			'weights': list(map(int, data[3::2])),
			'prices': list(map(int, data[4::2])),
		}
	ins.close()

	sol = open(solutions_file, 'r')
	for line in sol:
		data = line.split(' ')
		ins_id = int(data[0])
		instances[ins_id]['opt_sol'] = {
			'price': int(data[2]),
			'items': list(map(bool, map(int, data[4:]))),
		}
	sol.close()
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

def bf_rec(instance, depth, price, weight, items):
	if price > instance['bf_sol']['price'] and weight <= instance['capacity']:
		instance['bf_sol']['price'] = price
		instance['bf_sol']['weight'] = weight
		instance['bf_sol']['items'] = items[:]

	if depth < instance['size']:
		items[depth] = True
		bf_rec(instance, depth+1, price+instance['prices'][depth], weight+instance['weights'][depth], items)
		items[depth] = False
		bf_rec(instance, depth+1, price, weight, items)

def brute_force(instance, ins_id):
	instance['bf_sol'] = {
		'price': 0,
		'weight': 0,
		'items': [False for i in range(instance['size'])]
	}
	items = [False for i in range(instance['size'])]
	bf_rec(instance=instance, depth=0, price=0, weight=0, items=items)
	#~ if instance['bf_sol']['price'] != instance['opt_sol']['price'] or instance['bf_sol']['items'] != instance['opt_sol']['items']:
	#~ if instance['bf_sol']['price'] != instance['opt_sol']['price']:
		#~ print('{} failed \n\toptimal:    {}\n\tbrute force:{}'.format(ins_id, instance['opt_sol'], instance['bf_sol']))

def heur_ppw(instance, ins_id):
	data = [(i, instance['prices'][i]/instance['weights'][i]) for i in range(instance['size'])]
	data.sort(key=lambda item: item[1], reverse=True)
	pprint(data)
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
	type=click.Choice(['hw', 'hp', 'hppw', 'bf']), help='algorithm type'
)
def main(instances_file, solutions_file, time_measure, repeats, algorithm):
	instances = load_instances(instances_file, solutions_file)
	index = 1
	for key, instance in instances.items():
		if time_measure:
			start = time.time() 
		for i in range(repeats):
			if algorithm == 'bf':
				brute_force(instance, key)
			elif algorithm == 'hw':
				heur_weight(instance, key)
			elif algorithm == 'hp':
				heur_price(instance, key)
			elif algorithm == 'hppw':
				heur_ppw(instance, key)
		#~ pprint(instance)
		if time:
			print('time: {:0.3f}s'.format((time.time() - start)/repeats))
		index += 1
	#~ pprint(instances)
	return 0


if __name__ == '__main__':
	main()
