require 'unimidi'

notes = [36, 40, 43, 48, 52, 55, 60, 64, 67] # C E G arpeggios
duration = 0.1

output = UniMIDI::Output.open(:first)

output.open do |output|

  notes.each do |note|
    output.puts(0x90, note, 100) # note on message
    sleep(duration)  # wait
    output.puts(0x80, note, 100) # note off message
  end

end

input = UniMIDI::Input.first
input.open do |input|

  $stdout.puts "send some MIDI to your input now..."

  loop do
    m = input.gets
    $stdout.puts(m)
  end

end
