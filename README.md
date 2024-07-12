# Spanish Dialect Bias in Youtube's Captioning system
This repository contain my final project for the Advanced Method in Social Science class at the Univerisity of Munich. 

Recap so far: 
- [ ] I tried to upload them separely but I did exceed the daily Youtube's API quotas of videos that I can upload in a day, so I have created a one big .wav file with all the audios divided per gender together.
- [ ] Also changing in the internal structure to make worj easier(female and male rename for LATAM and female and male folder creation for spain).
- [ ] Concatenate and create the mapping.json file, all files will be saved in the data/interim folder
- [ ] now we need to convert the .wav into vidoes because yt only accept videos, to do so we will use a simple black image and convert from .wab to .mp4

TODO: 
- [ ] Upload stuff to youtube and get the captions
- [ ] Donwload the captions
- [ ] Also describe the part of setting up the Youtube part
- [ ] git clone
- [ ] requirements.txt 
- [ ] compare them to the trascript
- [ ] which metric to use?
- [ ] think of nice comparison and visualization(male vs female) --> how do i keep track of the females and male texts?
- [ ] maybe think if to use some metric from the class
- [ ] Nice repo(title, nice description)
- [ ] Link how to set up Youtube API
- [ ] Explain that videos will be longer than 15min, authentication is required 




## Data Download

Here you can Download the Datatsets:
[Argentina](https://www.openslr.org/61/), [Chile](https://www.openslr.org/71/), [Colombia](https://www.openslr.org/72/), [Spain](https://www.openslr.org/67/), [Peru](https://www.openslr.org/73/), [Puerto Rico](https://www.openslr.org/74/) and [Venezuela](https://www.openslr.org/75/). 
After the download you can put the data into the correspective folders. Note: There is no male audio for the Puerto Rico dataset. 

## Data preparation 

After downloading the data move them into the corresponding folders(all LATAM contries in the LATAM folder and extract the tedx_spain folder in the the spain folder). 
Move to the scripts directory since we will run all the scripts from here. 
```
cd scripts
```
and then execute the rename_and_move.py script
```
python rename_and_move.py
```

This script will create a nice structure of the data that will be easier to handle. 

Now, we are ready to manipulate the data. To do so, run the  concatenation_mapping.py script

```
python concatenation_mapping.py 
```
This script will concantenate all the different .wav audios files in one big audio for each contry and gender. It will also create a mapping .json file that will map the name of the audio, and its duration. We will need this later when comparing the generated caption to the ground truth text that we have. 

We now need to convert the .wav files into an audio because Youtube only accept videos and not audios, so we will just use a black image and upload the audio. To do this run 

```
python audio_to_video.py 
```

Now we can upload the video on Youtube by running

```
python upload_youtube.py
```
