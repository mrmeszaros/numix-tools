#!/usr/bin/env python
import click
import json
from colormath.color_objects import sRGBColor, HSLColor
from colormath.color_conversions import convert_color
# colormath
# - seems needs system python - https://github.com/pyenv/pyenv/issues/1474
# - mixing / blending is not supported - https://github.com/gtaylor/python-colormath/issues/4
import subprocess
from os import makedirs, symlink, system
from os.path import exists, expanduser
from shutil import copy
from glob import glob


@click.group()
def numix_helper():
	pass


# TODO: add global --version option
# TODO: move --quiet option to a global level
# TODO: add global -v/--verbose option
# TODO: make render --size and --shape accept comma separated options
# TODO: add autocompletion config
# - https://click.palletsprojects.com/en/7.x/bashcomplete/#activation-script
# TODO: add testing
# - https://click.palletsprojects.com/en/7.x/api/#testing
# TODO: try creating a point transformer (geometric transformations)
# - https://click.palletsprojects.com/en/7.x/commands/#multi-command-pipelines
# - check out the  in the geometry directory
# TODO: implement blend command if colormath supports it


SHAPES = ['circle', 'square']


def find_icon(name):
	prefix = f"{expanduser('~')}/.local/share/icons/hicolor"
	paths = glob(f"{prefix}/*/apps/{name}.png")
	size_map = {
		int(path[len(prefix)+1:].split('x')[0]): path
		for path in paths
	}
	return size_map[max(size_map.keys())]


@numix_helper.command('setup')
@click.argument('icon_name')
# FIXME renaming this option to --git might make more sense, since we are asking to setup git too
@click.option('create_branch', '-b', '--branch', help='Create and checkout git branch if not yet created', is_flag=True)
@click.option('original_name', '-o', '--original', help='Find the original icon and create a link')
def numix_setup(icon_name, create_branch, original_name):
	"""Set up links, files and git for new icon development"""
	if create_branch:
		system(f"git checkout -b {icon_name}")

	if original_name is not None:
		original_icon_path = find_icon(original_name)
		symlink(original_icon_path, f"{icon_name}.original.png")

	makedirs('ln', exist_ok=True)
	for shape in SHAPES:
		target = f"icons/{shape}/48/{icon_name}.svg"
		if not exists(target):
			copy(f"templates/{shape}/48.svg", target)
		link_path = f"ln/{icon_name}.{shape}.svg"
		if not exists(link_path):
			symlink(f"../{target}", link_path)


def git_current_branch_name():
	return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode('utf-8').strip()


def print_if(predicate, msg):
	if predicate:
		print(msg)


@numix_helper.command('render')
@click.argument('icon_names', nargs=-1)
@click.option('sizes', '-s', '--size', help='Specify the resolution of the raster.', multiple=True, type=int, default=[48], show_default=True)
@click.option('shapes', '-S', '--shape', help='Specify the shapes for which to render.', multiple=True, type=click.Choice(SHAPES), default=SHAPES, show_default=True)
@click.option('bundle', '-B', '--bundle', help='Create bundle images with all the shapes', is_flag=True)
@click.option('quiet', '-q', '--quiet', help='Diable all extraneous program output', is_flag=True)
def numix_render(icon_names, sizes, shapes, bundle, quiet):
	"""Render svg icons to raster images (png)"""
	if bundle:
		raise click.UsageError("Bundling is not implemented yet! Please contact the developer.")
	if len(icon_names) < 1:
		icon_names = [git_current_branch_name()]
	for icon_name in icon_names:
		print_if(not quiet, f"Rendering '{icon_name}' ...")
		for size in sizes:
			for shape in shapes:
				svg = f"icons/{shape}/48/{icon_name}.svg"
				png = f"{icon_name}.{shape}.{size}.png"
				if exists(svg):
					stdout = subprocess.check_output(["inkscape", svg, "-o", png, "-w", size, "2>&1"])
					# TODO log if verbose
					print_if(not quiet, f"... [DONE] {png}")
				else:
					print_if(not quiet, f"... [MISS] {png}")


def add_or_replace(base_value, input_value):
	if input_value.startswith(('+', '-')):
		return base_value + float(input_value)
	return float(input_value)


@numix_helper.command('color')
@click.argument('hex_colors', nargs=-1)
@click.option('hue', '-H', '--hue', help='Rotate the hue by/to the given value (0-360)')
@click.option('saturation', '-S', '--saturation', help='Change the saturation by/to the given value (0-100)')
@click.option('luminosity', '-L', '--luminosity', help='Change the luminosity by/to the given value (0-100)')
def numix_color(hex_colors, hue, saturation, luminosity):
	"""Change and display colors in various color spaces"""
	for hex_color in hex_colors:
		rgb = sRGBColor.new_from_rgb_hex(hex_color)
		hsl = convert_color(rgb, HSLColor)
		print(f'| {rgb.get_rgb_hex()} | hsl({hsl.hsl_h:.2f}, {hsl.hsl_s*100:.2f}%, {hsl.hsl_l*100:.2f}%) |')
		if hue:
			new_h = add_or_replace(hsl.hsl_h, hue)
			# Rotate back to 0-360
			hsl.hsl_h = new_h + 360*(new_h<0) - 360*(new_h>360)
		if saturation:
			new_s = add_or_replace(hsl.hsl_s*100, saturation)
			# Cut and scale into 0-1
			hsl.hsl_s = max(0, min(new_s, 100)) / 100
		if luminosity:
			new_l = add_or_replace(hsl.hsl_l*100, luminosity)
			# Cut and scale into 0-1
			hsl.hsl_l = max(0, min(new_l, 100)) / 100
		rgb = convert_color(hsl, sRGBColor)
		print(f'| {rgb.get_rgb_hex()} | hsl({hsl.hsl_h:.2f}, {hsl.hsl_s*100:.2f}%, {hsl.hsl_l*100:.2f}%) |')


class IconEntry:
	def __init__(self, entry):
		self._entry = entry

	def add_linux(self, name):
		if 'linux' not in self._entry:
			self._entry['linux'] = {'root': name}
		else:
			names = self._entry['linux'].get('symlinks', [])
			names.append(name)
			self._entry['linux']['symlinks'] = sorted(set(names))

	def add_android(self, name):
		names = self._entry.get('android', [])
		names.append(name)
		self._entry['android'] = sorted(set(names))


class IconDataBase:
	def __init__(self, file):
		self._file = file
		with open(file, 'r') as f:
			self._data = json.load(f)

	def __getitem__(self, name):
		if name not in self._data:
			self._data[name] = {}
		return IconEntry(self._data[name])

	def rename(self, name, new_name):
		self._data[new_name] = self._data.pop(name)

	def save(self):
		with open(self._file, 'w') as f:
			json.dump(self._data, f, indent=4, sort_keys=True)


@numix_helper.command('data')
@click.argument('icon_name')
@click.option('linux_entry', '-l', '--linux', help='Add linux (desktop icon) entry.')
@click.option('android_entry', '-a', '--android', help='Add android (app activity) entry.')
@click.option('new_icon_name', '-r', '--rename', help='Rename the icon entry.')
@click.option('registry_file', '-f', '--file', type=click.Path(exists=True), default='data.json', show_default=True, help='Use custom registry file.')
def numix_data(icon_name, linux_entry, android_entry, new_icon_name, registry_file):
	"""Add an entry to the icon name registry (data.json)"""
	if linux_entry or android_entry or new_icon_name:
		db = IconDataBase(registry_file)
		if linux_entry is not None:
			db[icon_name].add_linux(linux_entry)
		if android_entry is not None:
			db[icon_name].add_android(android_entry)
		if new_icon_name is not None:
			db.rename(icon_name, new_icon_name)
		db.save()
	else:
		print(f"Warning: no action specified, no changes made.")


if __name__ == '__main__':
	numix_helper()
