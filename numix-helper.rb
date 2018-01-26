#!/usr/bin/env ruby

# Dependencies:
# - color
# - commander
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


def show_color color
	puts "| ##{color.to_rgb.hex} | #{color.to_hsl.css_hsl}"
end

command :color do |c|
	c.syntax = 'numix color HEX_COLORS'
	c.option '-H', '--hue=H', Float, 'Rotate the hue by the given amount (0-360)'
	c.option '-S', '--saturation=S', Float, 'Change the saturation by the given amount (0-100)'
	c.option '-L', '--luminosity=L', Float, 'Change the luminosity by the given amount (0-100)'
	c.action do |args, options|
		args.each do |color|
			hsl = Color::RGB.by_hex(color).to_hsl
			show_color hsl
			hsl.hue += options.hue if options.hue
			hsl.saturation += options.saturation if options.saturation
			hsl.luminosity += options.luminosity if options.luminosity
			show_color hsl
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


command :render do |c|
	c.syntax = 'numix render ICON_NAME ...'
	c.description = 'Render svg icons to raster images (png)'
	c.option '-s', '--size SIZE', Integer, 'Specify the resolution of the raster.'
	c.option '-b', '--bundle', 'Create bundle images with all the shapes'
	c.option '-q', '--quiet', 'Diable all unnecessary program output'
	c.action do |args, options|
		options.default :size => 48
		args.each do |icon_name|
			puts "Rendering '#{icon_name}' ..." unless options.quiet
			pngs = []
			SHAPES.each do |shape|
				svg = "icons/#{shape}/48/#{icon_name}.svg"
				png = "#{icon_name}.#{shape}.#{options.size}.png"
				if File.file? svg
					`inkscape #{svg} -e #{png} -w #{options.size}`
					puts "... [DONE] #{png}" unless options.quiet
					pngs.push png
				else
					puts "... [MISS] #{svg}" unless options.quiet
				end
			end
			if options.bundle
				source = pngs.join(' ')
				target = "#{icon_name}.#{options.size}.png"
				`convert #{source} -rotate 90 -append -rotate -90 #{target}`
				puts "... [BUNDLE] #{target}" unless options.quiet
			end
		end
		notify_send 'Rendering finished!' if options.notify
	end
end
