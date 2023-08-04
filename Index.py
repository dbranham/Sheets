from pedalboard.io import AudioFile

# Replace "bach-prelude-c-major-156935.mp3" with the actual path to your audio file
audio_file_path = r"C:\Users\Andrew\Desktop\Sheets\bach-prelude-c-major-156935.mp3"



with AudioFile(audio_file_path) as f:
    audio = f.read(f.frames)
    audio[0]
    audio[1]
    audio[:, :100]
    audio[:, :f.samplerate * 10]
    audio[:, :-(f.samplerate * 10):]
    
    print("Samplerate:", f.samplerate)
    print("Number of Channels:", f.num_channels)
    print("hi")
    
