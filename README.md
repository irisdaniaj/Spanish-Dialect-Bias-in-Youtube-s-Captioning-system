# Spanish Dialect Bias in Youtube's Captioning system
This repository contain my final project for the Advanced Method in Social Science class at the Univerisity of Munich. 

TODO: 
- [ ] I tried to upload them separely but I did exceed the daily Youtube's API quotas of videos that I can upload in a day, so I have created a one big .wav file with all the audios divided per gender together.
- [ ] Also changing in the internal structure to make worj easier(female and male rename for LATAM and female and male folder creation for spain) 
- [ ] does the rename_and_move.py scripts really work????
- [ ] I have the audios so far, I need to convert them to videos.
- [ ] Upload them 
- [ ] do i need to clean the data? 
- [ ] Upload stuff to youtube and get the captions
- [ ] Donwload the captions
- [ ] compare them to the trascript
- [ ] which metric to use?
- [ ] think of nice comparison and visualization(male vs female) --> how do i keep track of the females and male texts?
- [ ] maybe think if to use some metric from the class
- [ ] Nice repo(title, nice description) 




## Data

Here you can Download the Datatsets:
[Argentina](https://www.openslr.org/61/), [Chile](https://www.openslr.org/71/), [Colombia](https://www.openslr.org/72/), [Spain](https://www.openslr.org/67/), [Peru](https://www.openslr.org/73/), [Puerto Rico](https://www.openslr.org/74/) and [Venezuela](https://www.openslr.org/75/). 
After the download you can put the data into the correspective folders. Note: There is no male audio for the Puerto Rico dataset. 

## Data preparation 

After downloading the data move them into the corresponding folders(all LATAM contries in the LATAM folder and extract the tedx_spain folder in the the spain folder). 
Move to the scripts directory 
```
cd scripts
```
and then execute the rename_and_move.py script
```
python rename_and_move.py
```

This script will create a nice structure of the data that will be easier to handle. 
