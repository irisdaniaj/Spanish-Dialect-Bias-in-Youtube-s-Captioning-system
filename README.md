# Gender and Dialect Bias in Youtube's Spanish Captioning system

Spanish is the official language of twenty-one countries and is spoken by over 441 million people. Naturally, there are many variations in how Spanish is spoken across these countries. However, YouTube offers only one option for automatically generating captions in Spanish. This raises the question: could this captioning system be biased against certain Spanish dialects? This study examines the potential biases in YouTube's automatic captioning system by analyzing its performance across various Spanish dialects. By comparing the performance of captions for female and male speakers from different regions, we aim to identify any systematic disadvantage faced by certain groups.

My research aims to answer this question. To do so, we will use Google's [Crowdsourcing Latin American Spanish for Low-Resource Text-to-Speech](https://aclanthology.org/2020.lrec-1.801.pdf) and the [TEDx Spanish Corpus](https://www.openslr.org/67/) datasets.




## Data Download

Here you can Download the Datatsets:
[Argentina](https://www.openslr.org/61/), [Chile](https://www.openslr.org/71/), [Colombia](https://www.openslr.org/72/), [Mexico](https://www.openslr.org/67/), [Peru](https://www.openslr.org/73/), [Puerto Rico](https://www.openslr.org/74/) and [Venezuela](https://www.openslr.org/75/). 
After the download you can put the data into the correspective folders. Note: There is no male audio for the Puerto Rico dataset. 

## Main 

Clone the repository 

```
git clone https://github.com/irisdaniaj/Spanish-Dialect-Bias-in-Youtube-s-Captioning-system.git
```
and create a conda environment using the environment.yml file 

```
conda env create -f environment.yml
conda activate dialect-bias
```
After downloading the data move them into the corresponding folders(Argentina, Chile, Colombia, Peru, Puerto Rico and Venezuela countries in the LATAM folder and extract the TEDx Spanish Corpus dataset in the Mexico folder). 
Move to the scripts directory since we will run all the scripts from here. 

```
cd src
```
and then execute 

```
python rename_and_move.py
```

This script will create a nice structure of the data that will be easier to handle. 

Now, we are ready to manipulate the data. To do so, run the  concatenation_mapping.py script

```
python concatenation_mapping.py 
```
This script will concantenate all the different .wav audios files in one big audio for each contry and gender of maximum 30 minutes with a five second delay between each audio. It will also create a mapping .json file that will map the name of the audio, and its duration. We will need this later when comparing the generated caption to the ground truth text that we have. 

NOTE: Youtube requires to authenticate your account if you post videos longer than 15 minutes, so if you plan to reproduce this work you will need to. More information [here](https://support.google.com/youtube/answer/71673?hl=en&co=GENIE.Platform%3DDesktop&oco=0). 

We now need to convert the .wav files into an audio because Youtube only accept videos and not audios, so we will just use a black image and upload the audio. To do this run 

```
python audio_to_video.py 
```

In the next part we will upload the videos via the Youtube's API and we will need to get a Youtube API key. More information [here](https://blog.hubspot.com/website/how-to-get-youtube-api-key). Please after step 7 make sure to dowlonad the "client_secret.json" file and place it in the same directory where you will run the script(scripts in this repo). 

Before uploading the first video, you will be prompted to choose a YouTube channel to upload the video to. Please select the same account that you have authorized in the previous steps.

I recommend creating a new YouTube channel specifically for uploading these videos because at the end of the process, we will download all the videos associated with the selected channel ID. This will help keep your uploads organized and separate from your main account. You can find more information on how to create a new YouTube channel [here](https://support.google.com/youtube/answer/1646861?hl=en)

Now we can upload the video on Youtube by running. 

```
python upload_youtube.py
```


NOTE: Youtube only allows to upload 6 videos each days via API, so to keep track of which videos have been uploaded to Youtube the script will also create an "uploaded_videos.json" file in which the title of the uploaded videos will be saved. So, next time we run the script we will first check which videos have already been uploaded to Youtube to not uploaded them twice. 

Now that the videos have been uploaded we can retrieve the generated captions. To do so we will need the ID of the Youtube channel in which we uploaded the videos. More information [here](https://support.google.com/youtube/answer/3250431?hl=en). 

```
python captions.py -YOUR_CHANNEL_ID
```
This will download the captions of all the video uploaded in the channel and it integrates the captions with existing metadata that maps the captions to specific files and speakers and then it saves the processed and integrated captions in JSON format "concatenated_audio_{country}_{gender}.json" in the results/intermediate/captions_integrated" folder. 

If you want to replicate the final results please run 

```
python analysis.py 
```

and

```
python analysis_mexico.py 
```

This script will generate .csv file that contains the filename, generated captions, treu transcription and the word error rate in the the results/final/summary folder along with some summary statistics. 

For the analysis of the prosedic features please run 

```
python audio_resample.py 
python audio_analysis.py
python audio_plot.py
```
For the modeling results please run 

```
python model.py 
```

## Acknowledgements 

I would to thank you Adrian David Castro Tenemaya for his technical support. 
