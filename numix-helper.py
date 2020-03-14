#!/usr/bin/env python
import click


@click.group()
def numix_helper():
	pass


@numix_helper.command('data')
def numix_data():
	"""Add an entry to the icon name registry (data.json)"""
	print('... Load data.json')
	print('... Add linux/android entry')
	print('... Save data.json')


if __name__ == '__main__':
	numix_helper()
