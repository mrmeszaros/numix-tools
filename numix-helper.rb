#!/usr/bin/env ruby

# Dependencies:
# - json
# - color
# - commander
require 'json'
require 'color'
require 'commander/import'


SHAPES = %w(circle square)

def notify_send message
	`notify-send -i numix '#{message}'`
end

program :name, 'Numix Helper'
program :version, '0.0.1'
program :description, 'Helper scripts for Numix icon development'
program :help, 'Author', 'Mészáros Máté Róbert <mateusz.meszaros@gmail.com>'

global_option('-n', '--notify', 'Send OS notification when the command finished')

default_command :help


def puts_color color, fmt
	puts fmt % {rgb: color.to_rgb.hex, hsl: color.css_hsl}
end

def calc_value base, change
	if change =~ /^[+-]/
		base + change.to_f
	else
		change.to_f
	end
end

command :color do |c|
	c.syntax = 'numix color HEX_COLORS...'
	c.option '-H', '--hue=H', String, 'Rotate the hue by the given amount (0-360)'
	c.option '-S', '--saturation=S', String, 'Change the saturation by the given amount (0-100)'
	c.option '-L', '--luminosity=L', String, 'Change the luminosity by the given amount (0-100)'
	c.option '-f', '--format=FORMAT', String, 'Format the output with the given ruby format string'
	c.action do |args, options|
		options.default :format => '| #%{rgb} | %{hsl} |'
		args.each do |color|
			hsl = Color::RGB.by_hex(color).to_hsl
			puts_color hsl, options.format
			hsl.hue = calc_value(hsl.hue, options.hue) if options.hue
			hsl.saturation = calc_value(hsl.saturation, options.saturation) if options.saturation
			hsl.luminosity = calc_value(hsl.luminosity, options.luminosity) if options.luminosity
			puts_color hsl, options.format
		end
	end
end

command :blend do |c|
	c.syntax = 'numix blend COLOR1 COLOR2 [options]'
	c.option '-f', '--format=FORMAT', String, 'Format the output with the given ruby format string'
	c.option '-r', '--ratio=RATIO', Array, 'Use given ratios to blend the colors'
	c.action do |args, options|
		options.default :format => '| %{r} | %{rgb} | %{hsl} |', :ratio => [0.5]
		if args.size != 2
			puts "[ERROR]: The blend command expects exactly 2 arguments!"
		else
			c1 = Color::RGB.by_hex(args[0]).to_hsl
			c2 = Color::RGB.by_hex(args[1]).to_hsl
			options.ratio.each do |r|
				mixture = c1.mix_with(c2, r.to_f)
				puts options.format % {r: r, rgb: mixture.to_rgb.hex, hsl: mixture.css_hsl}
			end
		end
	end
end


command :setup do |c|
	c.syntax = 'numix setup ICON_NAME [options]'
	c.description = 'Set up links for a new icon'
	c.option '-r', '--rename LINK_NAME', String, 'Rename the link (Defaults to ICON_NAME)'
	c.option '-b', '--branch', 'Create git branch named LINK_NAME if not yet created'
	c.action do |args, options|
		icon_name = args.first
		link_name = options.rename || icon_name
		`git checkout -b #{link_name}` if options.branch && `git branch --list #{link_name}`.empty?
		Dir.mkdir('ln') unless File.directory?('ln')
		SHAPES.each do |shape|
			target = "icons/#{shape}/48/#{icon_name}.svg"
			`cp templates/#{shape}/48.svg #{target}` unless File.file? target
			`ln -s ../#{target} ln/#{link_name}.#{shape}.svg`
		end
		notify_send 'Setup finished!' if options.notify
	end
end


DATA_JSON = 'data.json'

class Hash
	def sorted!
		self.keys.sort_by{ |k| k.downcase }.each { |k| self[k] = self.delete k }
	end
end

class Array
	def insert_sorted item
		idx = (0...self.size).bsearch{ |i| item.downcase < self[i].downcase } || self.size
		self.insert idx, item
	end
end

class IconEntry
	def initialize entry
		@hash = entry
	end

	def linux icon
		unless @hash.include? 'linux'
			@hash['linux'] = { 'root' => icon }
			@hash.sorted!
		else
			@hash['linux']['symlinks'] = [] unless @hash['linux'].include? 'symlinks'
			@hash['linux']['symlinks'].insert_sorted icon
		end
	end

	def android icon
		unless @hash.include? 'android'
			@hash['android'] = []
			@hash.sorted!
		end
		@hash['android'].insert_sorted icon
	end
end

class IconData
	def initialize file
		@file = file
		@data = JSON[File.read file]
	end

	def [] icon
		@data[icon] = {} unless @data.include? icon
		IconEntry.new @data[icon]
	end

	def rename old_name, new_name
		@data[new_name] = @data.delete old_name
	end

	def save!
		@data = @data.sort_by{ |k,v| k.downcase }.to_h
		json = JSON.pretty_generate @data, indent: "\t"
		File.open(@file, 'w') { |file| file.write(json + "\n") }
	end
end

command :data do |c|
	c.syntax = 'numix data ICON_NAME [options]'
	c.description = 'Add data entry for the icon'
	c.option '-l', '--linux=ENTRY', String, 'Add linux entry (root or symlink)'
	c.option '-a', '--android=ENTRY', String, 'Add android entry (root or symlink)'
	c.option '-r', '--rename=ICON_NAME', String, 'Rename the data entry base name'
	c.action do |args, options|
		icon_name = args.first
		if options.linux or options.android or options.rename
			data = IconData.new DATA_JSON
			data[icon_name].linux options.linux if options.linux
			data[icon_name].android options.android if options.android
			data.rename icon_name, options.rename if options.rename
			data.save!
		end
	end
end


command :render do |c|
	c.syntax = 'numix render ICON_NAME ...'
	c.description = 'Render svg icons to raster images (png)'
	c.option '-s', '--size SIZES', Array, 'Specify the resolution of the raster.'
	c.option '-b', '--bundle', 'Create bundle images with all the shapes'
	c.option '-q', '--quiet', 'Diable all unnecessary program output'
	c.action do |icon_names, options|
		options.default :size => [48]
		sizes = options.size.map(&:to_i).sort.reverse
		icon_names.each do |icon_name|

			puts "Rendering '#{icon_name}' ..." unless options.quiet
			pngs = sizes.map{ |s| [s, []] }.to_h
			sizes.each do |size|
				SHAPES.each do |shape|
					svg = "icons/#{shape}/48/#{icon_name}.svg"
					png = "#{icon_name}.#{shape}.#{size}.png"
					if File.file? svg
						`inkscape #{svg} -e #{png} -w #{size}`
						puts "... [DONE] #{png}" unless options.quiet
						pngs[size].push png
					else
						puts "... [MISS] #{svg}" unless options.quiet
					end
				end
			end

			if options.bundle
				parts = []
				sizes.each do |size|
					source = pngs[size].join(' ')
					target = "#{icon_name}.#{size}.png"
					padding = (sizes.max - size) / 2.0
					`convert #{source} -bordercolor none -border #{padding}x4 -rotate 90 -append -rotate -90 #{target}`
					puts "... [BUNDLE] #{target}" unless options.quiet
					parts.push target
				end
				if 1 < sizes.size
					source = parts.join(' ')
					target = "#{icon_name}.#{sizes.join('-')}.png"
					`convert #{source} -append #{target}`
					puts "... [BUNDLE] #{target}" unless options.quiet
					`rm #{source}` if options
				end
			end

		end
		notify_send 'Rendering finished!' if options.notify
	end
end
