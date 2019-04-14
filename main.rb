require 'unimidi'

NOTE_ON = 144
NOTE_OFF = 128

puts "Inputs:"
UniMIDI::Input.list

puts "Outputs:"
UniMIDI::Output.list


notes = [36, 40, 43, 48, 52, 55, 60, 64, 67] # C E G arpeggios
duration = 0.1

output = UniMIDI::Output.use(0)
puts "Writing to: #{output.pretty_name}"
input = UniMIDI::Input.use(1)


TRANSFORM_KEY = {
    # see Dorian: https://www.youtube.com/watch?v=zKdWSYcApD0
    dorian: {
        # 2 4 5 7 9 11 12
        0 => 2, # C
        1 => 0,
        2 => 4, # D
        3 => 0,
        4 => 5, # E
        5 => 7, # F
        6 => 0,
        7 => 9, # G
        8 => 0,
        9 => 11, # A
        10 => 0,
        11 => 12 # B
    }
}

output.open do |output|

  notes.each do |note|
    output.puts(NOTE_ON, note, 100) # note on
    sleep(duration)
    output.puts(NOTE_OFF, note, 100) # note off message
  end

  puts "Reading from: #{input.pretty_name}"
  input.open do |input|
    loop do
      m = input.gets
      if m.length > 0
        data = m[0][:data]
        type = data[0]
        note = data[1]
        vel = data[2]

        octave = note / 12
        key = note % 12
        new_key = TRANSFORM_KEY[:dorian][key] || 0

        output.puts(type, octave * 12 + new_key, vel)
        # puts "#{type} note=#{note} #{vel}"
      end
    end

  end
end
