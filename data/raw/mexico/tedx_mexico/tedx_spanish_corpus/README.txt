-------------------------------------------------------------------------------------------------
                                   TEDx Spanish Corpus
                 Audio and Transcripts in Spanish taken from the TEDx Talks
-------------------------------------------------------------------------------------------------

-------------------------------------------------------------------------------------------------
PRESENTATION
-------------------------------------------------------------------------------------------------

According to the TEDx website (https://www.ted.com/tedx/events/17437):

In the spirit of ideas worth spreading, TEDx is a program of local, self-organized events that 
bring people together to share a TED-like experience. At a TEDx event, TEDTalks video and live 
speakers combine to spark deep discussion and connection in a small group. These local, 
self-organized events are branded TEDx, where x = independently organized TED event. The TED 
Conference provides general guidance for the TEDx program, but individual TEDx events are 
self-organized (subject to certain rules and regulations).

Therefore, the TEDx Spanish Corpus is a dataset created from TEDx talks in Spanish and it
aims to be used in the Automatic Speech Recognition (ASR) Task.

The TEDx Spanish Corpus is a gender unbalanced corpus of 24 hours of duration. It contains 
spontaneous speech of several expositors in TEDx events; most of them are men.

-------------------------------------------------------------------------------------------------
TERMS OF USE
-------------------------------------------------------------------------------------------------

TEDx Spanish Corpus by Carlos Daniel Hernández Mena is licensed under a 
Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International License. 
To view a copy of this license visit https://creativecommons.org/licenses/by-nc-nd/4.0/
Based on a work at https://www.ted.com/watch/tedx-talks

-------------------------------------------------------------------------------------------------
CORPUS CHARACTERISTICS
-------------------------------------------------------------------------------------------------

The TEDx Spanish Corpus (TSC) has the following characteristics:

- The TSC has an exact duration of 24 hours and 29 minutes. It has 11243 audio files.

- The TSC counts with 142 different speakers: 102 men and 40 women. 

- Every audio file in the TSC has a duration between 3 and 10 seconds approximately.

- Data in TSC is classified by speaker. It means, all the recordings of one single
  speaker are stored in one single directory.

- Data is also classified according to the gender (male/female) of the speakers.

- Audio and transcriptions in the TSC are segmented and transcribed by native speakers of
  the Spanish language

- Audio files in the TSC are distributed in a Windows WAVE 16khz@16bit mono format.

- Every audio file has an ID that is compatible with ASR engines such as Kaldi and CMU-Sphinx.

-------------------------------------------------------------------------------------------------
GENERAL ORGANIZATION OF THE DIRECTORIES
-------------------------------------------------------------------------------------------------

The TEDX_SPANISH directory contains the following files and directories:

	- files	: 	One can find the transcription file, the paths file as well as the 
			"Speaker_Info.xls" file that contains relevant information about
                        all the sepakers in the corpus.

	- speech:	One can find the speech files.

	- LICENSE.txt

	- README.txt

-------------------------------------------------------------------------------------------------
THE CORPUS FILES
-------------------------------------------------------------------------------------------------

In the "files" directory one can find the following:

- TEDx_Spanish.transcription	        : This is the transcription file in plain text format.

- TEDx_Spanish.paths	        	: This file contains the relative paths from the
					  "speech" directory to every particular speech file.

- Speaker_Info.xls			: This file contains relevant information about the 
					  speakers. Specifically: Number of audios per speaker 
                                          and the total amount of time of speech per speaker.

-------------------------------------------------------------------------------------------------
IDENTIFICATION KEY FORMAT
-------------------------------------------------------------------------------------------------

Every audio file in the TEDx Spanish Corpus has an identification key with the following 
format:
                                 TEDX_M_001_SPA_0001

	TEDX            M            001            SPA                0001
      Acronym      Gender of        Number        Spanish            Number of the
      for          the Speaker:      of           Language           audio file of
      "TEDx        "M" for Male     Speaker.                         a particular
      Talks"       "F" for Female                                    speaker.

-------------------------------------------------------------------------------------------------
ACKNOWLEDGEMENTS
-------------------------------------------------------------------------------------------------

The author would like to thank to Alejandro V. Mena, Elena Vera and Angélica Gutiérrez for their 
support to the social service program: "Desarrollo de Tecnologías del Habla." He also thanks 
to the social service students for all the hard work.

Special thanks to the TEDx Team team for publishing all the recordings that constitute the 
TEDx Spanish Corpus.

-------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------
                  To find Corpora similar to this visit: www.ciempiess.org
-------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------

