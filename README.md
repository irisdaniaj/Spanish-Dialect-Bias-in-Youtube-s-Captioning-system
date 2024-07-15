# Spanish Dialect Bias in Youtube's Captioning system

Spanish is the official language of 21 countries and is spoken by over 441 million people. Naturally, there are many variations in how Spanish is spoken across these countries. However, YouTube offers only one option for generating captions in Spanish. This raises the question: could this captioning system be biased against certain Spanish dialects?

My research aims to answer this question. To do so, we will use Google's [Crowdsourcing Latin American Spanish for Low-Resource Text-to-Speech](https://aclanthology.org/2020.lrec-1.801.pdf) and the [TEDx Spanish Corpus](https://www.openslr.org/67/) datasets.




## Data Download

Here you can Download the Datatsets:
[Argentina](https://www.openslr.org/61/), [Chile](https://www.openslr.org/71/), [Colombia](https://www.openslr.org/72/), [Spain](https://www.openslr.org/67/), [Peru](https://www.openslr.org/73/), [Puerto Rico](https://www.openslr.org/74/) and [Venezuela](https://www.openslr.org/75/). 
After the download you can put the data into the correspective folders. Note: There is no male audio for the Puerto Rico dataset. 

## Main 

Clone the repository 

```
git clone https://github.com/irisdaniaj/Spanish-Dialect-Bias-in-Youtube-s-Captioning-system.git
```
and create a conda environment using the requirements.txt file 

```
conda create --name myenv python=3.9
conda activate myenv
pip install -r requirements.txt
```
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
python analysis_spain.py 
```

This script will generate .csv file that contains the filename, generated captions, treu transcription and the word error rate in the the results/final/summary folder along with some summary statistics. 

## Results 


The following Table report the Word-Error-rate(WER) for each country and gender. The WER is the ratio of errors in a transcript to the total words spoken. A lower WER in speech-to-text means better accuracy in recognizing speech. For example, a 20% WER means the transcript is 80% accurate. 

| Country | WER Female | WER Male |
|----------|----------|----------|
| Argentina | 0.24 | 0.23 |
| Chile | 0.21 | 0.22 |
| Colombia | 0.22 | 0.22 |
| Spain | 0.19 | 0.20 |
| Peru | 0.20 | 0.20  |
| Puero Rico | 0.16 | - |
| Venezuela | 0.23 | 0.21 |

The best captions are generated for females speaker from Puerto Rico, while the worst performance is achieved for Argentinian females speakers.

| Country | WER  | 
|----------|----------|
| Argentina | 0.24 | 
| Chile | 0.22 | 
| Colombia | 0.22 | 
| Spain | 0.20 | 
| Peru | 0.20 | 
| Puero Rico | 0.16 |
| Venezuela | 0.22 | 

The best perfomance is achieved by speakers from Puerto Rico, while speakers from Argentina have the highest WER score. The difference between the best and worst perfomance is 0.08 indicating a noticeable gap in the quality of the generated captions. 

## Limitations and Future Directions 

**Computational Resources**

One of the primary challenges we face is managing computational resources. Processing and analyzing large volumes of audio data, converting them into video format, and running comparisons between YouTube captions and ground truth transcriptions require significant computing power, which I did not have access to. Consequently, the videos are limited to 30 minutes each, even though we have hours of audio available for each country. In the future, it will be interesting to upload longer videos to fully utilize the available audio data.

**YouTube API Limitations**

An important consideration is the limitations imposed by the YouTube API. While the API enables automated video uploads and caption retrieval, it restricts the number of requests that can be made within a specific time frame. These restrictions can slow down data processing and analysis, necessitating strategic planning of uploads and retrievals to avoid exceeding these limits. For example, I was able to upload only six videos per day via the API, and there is also a cap on the number of videos one can upload manually through YouTube Studio. Additionally, the YouTube credit system limits the number of captions that can be retrieved in a day, which significantly slowed my progress.

**Geographic Coverage**

Geographic coverage is another crucial aspect. Our dataset includes various Spanish dialects from different regions, but ensuring comprehensive coverage is challenging. Some dialects may be underrepresented, which can impact the robustness of our analysis. Expanding the dataset to include a broader range of dialects from more countries will improve the reliability of our findings and provide a more thorough assessment of potential biases in YouTube's captioning system.

**Identifying Specific Sounds**

It would be interesting to explore whether there are specific sounds in the Spanish Dialects that YouTube's captioning system struggles with more than others. Identifying these problematic sounds could provide insights into the system's limitations and areas for improvement.

**Comparative Analysis**

A broader comparative analysis of YouTube's captioning system across different languages could also be valuable. By comparing the accuracy of captions in various languages, we can gain a deeper understanding of the system's performance and potential biases. This could help in identifying areas where the captioning system may need adjustments to better handle linguistic diversity.



## Note 

This repository contain my final project for the Advanced Method in Social Science class at the Univerisity of Munich. 
