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
	if instance['bf_sol']['price'] != instance['opt_sol']['price']:
		print('{} failed \n\toptimal:    {}\n\tbrute force:{}'.format(ins_id, instance['opt_sol'], instance['bf_sol']))


@click.command()
@click.option(
	'--instances-file',
	type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True),
	help='path to file with instances', prompt='Enter path to file with instances'
)
@click.option(
	'--solutions-file',
	type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True),
	help='path to file with solutions', prompt='Enter path to file with solutions'
)
def main(instances_file, solutions_file):
	instances = load_instances(instances_file, solutions_file)
	index = 1
	for key, instance in instances.items():
		start = time.time()
		brute_force(instance, key)
		#~ print(instance)
		print('{} of {}, time {:0.3f}s'.format(index, len(instances), time.time() - start))
		index += 1
	#~ pprint(instances)
	return 0


if __name__ == '__main__':
	main()
