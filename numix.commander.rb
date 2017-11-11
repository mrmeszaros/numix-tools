#!/usr/bin/env ruby

require 'commander/import'
require 'color'

SHAPES = %w(circle square)

def notify_send message
	`notify-send -i numix '#{message}'`
end

def icon_path name, shape
	link = "ln/#{name}.#{shape}.svg"
	File.exists?(link) ? link : "./icons/#{shape}/48/#{name}.svg"
end

program :name, 'Numix Helper'
program :version, '0.0.1'
program :description, 'Helper scripts for Numix icon development'
program :help, 'Author', 'Mészáros Máté Róbert <mateusz.meszaros@gmail.com>'

global_option('-n', '--notify', 'Send OS notification when the command finished')

default_command :help

command :setup do |c|
	c.syntax = 'numix setup ICON_NAME [options]'
	c.description = 'Set up links for a new icon'
	c.option '-r', '--rename LINK_NAME', String, 'Rename the link (Defaults to ICON_NAME)'
	c.option '-b', '--branch', 'Create git branch named LINK_NAME if not yet created'
	c.action do |args, options|
		icon_name = args.first
		link_name = options.rename || icon_name
		`git checkout -b #{link_name}` if options.branch && `git branch --list #{link_name}`.empty?
		SHAPES.each do |shape|
			`ln -s ../icons/#{shape}/48/#{icon_name}.svg ln/#{link_name}.#{shape}.svg`
		end
		notify_send 'Setup finished!' if options.notify
	end
end

command :render do |c|
	c.syntax = 'numix render ICON_NAME ...'
	c.description = 'Render svg icons to raster images (png)'
	c.option '-s', '--size SIZE', Integer, 'Specify the resolution of the raster.'
	c.option '-b', '--bundle', 'Create bundle images with all the shapes'
	c.action do |args, options|
		option_size = "-w #{options.size}" if options.size
		raster_size = ".#{options.size}" if options.size
		args.each do |icon_name|
			SHAPES.each do |shape|
				icon = icon_path icon_name, shape
				if File.file? icon
					`inkscape #{icon} -e #{icon_name}.#{shape}#{raster_size}.png #{option_size}`
				else
					puts "Not found: #{icon}"
				end
			end
			if options.bundle
				source = Dir["#{icon_name}.{#{SHAPES.join(',')}}#{raster_size}.png"].join(' ')
				target = "#{icon_name}#{raster_size}.png"
				`convert #{source} -rotate 90 -append -rotate -90 #{target}`
			end
		end
		notify_send 'Rendering finished!' if options.notify
	end
end
