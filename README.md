# Hank-Bot 
Hank-Bot is an automation application that records computer actions to allow a user to automate 
inputs to programs. It records the actions then outputs them as a Json file to later be read when the 
user wishes to play them back. The program also has a simple editor to edit and save the playback 
file in the case of errors. Thus, allowing an end user more power over the fine tuning of the recorded 
files.

### Prerequisites
There are no further prequisites required for running the software other than what is included in
the build folder.

### Installing
The executable file for the current build of the project is in the [build](build) folder.

You can find a simple tutorial video on the download and installation of the program [here](https://www.youtube.com/watch?v=5_o-bEVHiZc&ab_channel=JeffreyHale). There are
further tutorial videos below of basic usage of the program in the tutorials section.

If you run into trouble with your antivirus terminating the program check out my video on how I dealt with Microsoft Defender and running the program in administrator mode [here](https://www.youtube.com/watch?v=zvxAE-eJf7Y&list=PLz6kVqNDu0s4YAqfidFvaBESzpjFQqALj&index=2&ab_channel=JeffreyHale).
If you are still running into trouble after that look into your current antivirus and how to add the program to its exclusion list.

## Testing
Most of my testing was practical in nature. You can find the videos covering my testing below.

- Testing the keyboard inputs available [here](https://www.youtube.com/watch?v=6l5ru9JL3Ow&list=PLz6kVqNDu0s5uoFad-g-VEpj_bLU7Igo1&index=1&ab_channel=JeffreyHale)
- Testing the mouse inputs like drag and drop [here](https://www.youtube.com/watch?v=pw0r9Hp59-w&list=PLz6kVqNDu0s5uoFad-g-VEpj_bLU7Igo1&index=2&ab_channel=JeffreyHale)
- Testing the load and saving features [here](https://www.youtube.com/watch?v=AJvGn4iqce0&list=PLz6kVqNDu0s5uoFad-g-VEpj_bLU7Igo1&index=3&ab_channel=JeffreyHale)
- Testing the practical application of gameplay [here](https://www.youtube.com/watch?v=PsRcLY9eDjo&list=PLz6kVqNDu0s5uoFad-g-VEpj_bLU7Igo1&index=4&ab_channel=JeffreyHale)

## Tutorials
The following are some basic usages for the program and how to best enact them.

- Simple typed email drafting and reply [here](https://www.youtube.com/watch?v=OrnVCwyJptI&ab_channel=JeffreyHale).
- Part one of showing basic recording in a video game [here](https://www.youtube.com/watch?v=HJ8QXlwCxjw&ab_channel=JeffreyHale).
- Part two showing some longer recordings and how to best enact them in a video game [here](https://www.youtube.com/watch?v=v_V_Kw_sDu8&ab_channel=JeffreyHale).

## Built With

- [PyQt5](https://pypi.org/project/PyQt5/) - For the gui.
- [Pynput](https://github.com/moses-palmer/pynput) - For the listeners for the input actions.
- [Pydirectinput](https://github.com/learncodebygaming/pydirectinput) - For the playback of the actions.

## Author
Jeff Hale

Senior Capstone Project for Computer Science at Northeastern State University

## License
This project is licensed under the MIT License – see the [LICENSE.md](LICENSE) file for details 

## Acknowledgements
- This program was built using functions from this project [here](https://github.com/learncodebygaming/enb_bot) by [learncodebygaming](https://github.com/learncodebygaming).
