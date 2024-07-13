# Spanish Dialect Bias in Youtube's Captioning system

Spanish is the official language of 21 countries and is spoken by over 441 million people. Naturally, there are many variations in how Spanish is spoken across these countries. However, YouTube offers only one option for generating captions in Spanish. This raises the question: could this captioning system be biased against certain Spanish dialects?

My research aims to answer this question. To do so, we will use Google's [Crowdsourcing Latin American Spanish for Low-Resource Text-to-Speech](https://aclanthology.org/2020.lrec-1.801.pdf) datasets.

This repository contain my final project for the Advanced Method in Social Science class at the Univerisity of Munich. 

Recap so far: 
- [ ] I tried to upload them separely but I did exceed the daily Youtube's API quotas of videos that I can upload in a day, so I have created a one big .wav file with all the audios divided per gender together.
- [ ] Also changing in the internal structure to make worj easier(female and male rename for LATAM and female and male folder creation for spain).
- [ ] Concatenate and create the mapping.json file, all files will be saved in the data/interim folder
- [ ] now we need to convert the .wav into vidoes because yt only accept videos, to do so we will use a simple black image and convert from .wab to .mp4

TODO: 
- [ ] Upload stuff to youtube and get the captions
- [ ] Donwload the captions
- [ ] git clone
- [ ] requirements.txt 
- [ ] compare them to the trascript
- [ ] which metric to use?
- [ ] think of nice comparison and visualization(male vs female) --> how do i keep track of the females and male texts?
- [ ] maybe think if to use some metric from the class
- [ ] Nice repo(title, nice description)
- [ ] force to create new channel




## Data Download

Here you can Download the Datatsets:
[Argentina](https://www.openslr.org/61/), [Chile](https://www.openslr.org/71/), [Colombia](https://www.openslr.org/72/), [Spain](https://www.openslr.org/67/), [Peru](https://www.openslr.org/73/), [Puerto Rico](https://www.openslr.org/74/) and [Venezuela](https://www.openslr.org/75/). 
After the download you can put the data into the correspective folders. Note: There is no male audio for the Puerto Rico dataset. 

## Main part 

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
This script will concantenate all the different .wav audios files in one big audio for each contry and gender of maximum 30 minutes. It will also create a mapping .json file that will map the name of the audio, and its duration. We will need this later when comparing the generated caption to the ground truth text that we have. 

NOTE: Youtube requires to authenticate your account if you post videos longer than 15 minutes, so if you plan to reproduce this work you will need to. More information [here](https://support.google.com/youtube/answer/71673?hl=en&co=GENIE.Platform%3DDesktop&oco=0). 

We now need to convert the .wav files into an audio because Youtube only accept videos and not audios, so we will just use a black image and upload the audio. To do this run 

```
python audio_to_video.py 
```

In the next part we will upload the videos via the Youtube's API and we will need to get a Youtube API key. More information [here](https://blog.hubspot.com/website/how-to-get-youtube-api-key). Please after step 7 make sure to dowlonad the "client_secret.json" file and place it in the same directory where you will run the script(scripts in this repo). 

Now we can upload the video on Youtube by running

```
python upload_youtube.py
```
Before uploading the first video you will be asked to choose a Youtube channel to upload the video to. Please select the same account that you have authorize in the steps before. If you want to create a new Youtube channel just to upload this videos you can do so(I highly suggest it). More information [here](https://support.google.com/youtube/answer/1646861?hl=en). 

NOTE: Youtube only allows to upload 6 videos each days via API, so to keep track of which videos have been uploaded to Youtube the script will also create an "uploaded_videos.json" file in which the title of the uploaded videos will be saved. So, next time we run the script we will first check which videos have already been uploaded to Youtube to not uploaded them twice. 

Now that the videos have been uploaded we can retrieve the generated captions

