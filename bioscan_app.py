"""
Date Created: 10/04/2022
Last Modified: 11/27/2022
Purpose:
    The web app file for BioScan. Uses streamlit. 
    Application takes an image from user and classifies the category of skin condition that 
        it belongs to by running it through our model. Provides additional info and links on
        the skin condition as well.
"""

#===================================Imports=======================================
#Library Imports
import streamlit as st #streamlit is the web platform used to host our webapp. The library is for interacting with it & creating the webpage.
import matplotlib.pyplot as plt #matplotlib is for producing graphs. Used to make the pie chart for the output results.
import numpy as np #numpy is a data science library for formatting data in a clean way. Needed to analyze output because tensorflow models utilize numpy arrays.
import tensorflow as tf #Tensorflow is the machine learning library used to create models. Needed to upload and run the model on the webapp.
import cv2 #OpenCV is a library that provides the capability of opening and editing image files within python. Used to upload images to the model.
from PIL import Image #PIL is another library for opening images in python. Needed to open the image from user input to pass it off to cv2 for editing.
import pandas as pd #Pandas is another data science tool for python. Like numpy, used to read tensorflow model output.

#Class Import
from conditions import Conditions #Our conditions class. Used to pass information on the specific condition to the webapp based upon the model's results

#=========================Importing the model=================================
model = tf.keras.models.load_model('epoch_2500.hdf5') #Imports the ml model to utilize by the webapp. Opens from the binary file epoch_2500.hdf5 also within the github.

#=============================Constant Variables==================================
#Image Constants
IMAGE_SIZE = (150, 150) #Constant for image size

#Webapp Text formatting constants
#All are used to provide specific html formatting throughout the webpage. Used to prevent the need to retype the information
basic = '<p style="font-family:Georgia; color:Black; font-size: 24px;">'
basicbold = '<p style="font-family:Georgia; font-weight: bold; color:Black; font-size: 24px;">'
header = '<p style="font-family:Georgia; color:Black; font-size: 44px;">'
subheader = '<p style="font-family:Georgia; font-weight: bold; color:Black; font-size: 24px;">'
title = '<p style="font-family:Georgia; font-weight: bold; color:Black; font-size: 58px;">'

#==================================Functions==========================================
def image_conversion(image):
    """
    Inputs: image (jpeg or png)
    Outputs: data array
    Creation Date: 10/04/2022
    Purpose:
        Processes a provided image so that it can be input into a model.
    """

    image = np.array(image) #Stores the image in a numpy array. Needed for passing to cv2 and later the ml model.
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #Converts image to RGB. Better for model.
    image = cv2.resize(image, IMAGE_SIZE) #Resizes the image to a standard size for the model.
    image = image.reshape(1, image.shape[0], image.shape[1], image.shape[2]) #reshapes the data array for the size of the image to fit the model's formatting requirements.

    return image #Returns the formatted image. 

def run_model(image, model):
    """
    Inputs: image, tensoflow model (.hdf5 file)
    Outputs: np array
    Creation Date: 10/04/2022
    Purpose: Takes a provided image and runs it through the provided tensorflow machine learning model.
    """
    conversion = image_conversion(image) #Runs the image conversion function to convert the provided image to the proper format to be read by the model.
    return model.predict(conversion) #Runs the model's predict method with the converted image as an input. Returns the prediction array provided by the model.

def average_predictions(predictions):
    """
    Inputs: A list of prediction outputs generated by passing images into the model.
    Outputs: A list of lists containing the averages for the benign prediction weights and the malignant prediction weights
    Creation Date: 11/26/2022
    Purpose: Provides the average prodiction weights when multiple images are passed to the model and thus multiple results are generated.
    """
    malig_val = 0 #Initializes malignant total weight to start at zero
    benign_val = 0 #Initializes the benign total weight to start at zero
    for prediction in predictions:
        #Iterates through the predictions list passed to the function to sum up both the malignant and benign weights.
        malig_val += prediction[0][1] #Takes each malignant prediction weight and stores it in the malig_val variable
        benign_val += prediction[0][0] #Takes each benign prediction weight and stores it in the benign_val veriable.
    avg_malig_val = malig_val/len(predictions) #Averages the prediction for malignant based on the number of images provided
    avg_benign_val = benign_val/len(predictions) #Averages the prediction for benign based on the number of images provided
    return [[avg_benign_val, avg_malig_val]] #Returns the averages as a list of lists to maintain the output formating produced by the model.

#================================Webpage Code====================================
#Code for the importing the background image.
#Needed for providing streamlit with the css formating it needs to use the image. Syntax is streamlit specific.
import base64
def background(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
background('background_img.jpg')

#Wepage Text
#Initial webpage text. Provides webpage title, explanation, and instructions.
st.markdown(title + 'BioScan' + "</p>", unsafe_allow_html=True)
st.markdown(header + 'An image classifier.\n\n' + "</p>", unsafe_allow_html=True)
st.sidebar.subheader('Disclaimer')
st.sidebar.write('This is a program created by four computer science students who are not capable of giving valid medical advaice.')
st.sidebar.write('Please do not use this site for valid medical advice. ')
st.sidebar.write('If you are in doubt about your health see a doctor!')
st.markdown(header + 'Instructions:' + "</p>", unsafe_allow_html=True)
st.markdown(subheader + 'To use BioScan take a picture of your skin condition and save it as a jpg or png.' + "</p>", unsafe_allow_html=True)
st.markdown(basic + 'Import the image below.' + "</p>", unsafe_allow_html=True)

#Prompts user to upload a file.
options = ['File Upload', 'WebCam Upload'] #Creates a list with the upload option text.
option = st.radio('Select an option:', options) #Creates radio selection of the upload options on the webapp. Allows user to select only one.
if option == 'File Upload': #If the user selected to upload via file upload, promts them to input a file.
    user_image_list = st.file_uploader("Please upload an image file", type = ["jpg", "png"], accept_multiple_files=True) #Uses streamlits built in file uploader to input an image file. Already has built in functionality for adding multiple images.
else: #If the user did not choose to input from a file, meaning they instead chose to input using their camera.
    user_image = st.camera_input("Take a picture") #Calls streamlits built in camera method.
    user_image_list = [] #Creates a list for storing multiple camera uploads as this is not built into streamlit by default.
    if user_image: #If the user provided an image. Stores it in the image list.
        user_image_list.append(user_image)

#Space formatting for text of the webapp
st.text('')
st.text('')

#Optional survery so user is able to add symptoms they are experiencing to create more accurate results
st.markdown(subheader + 'Supplementary Survey:' + "</p>", unsafe_allow_html=True) #Text presenting the survey to the user.   
counter = 0 #Counter for keeping track fo user results.
st.markdown(basic + 'Complete the optional Survey below based on the symptoms you are experiencing:' + "</p>", unsafe_allow_html=True) #Instruction text for the survey.
#Presents the survery as a dropdown of different potential conditions that the user can select from. Allows selecting of multiple conditions
options = st.multiselect( " ",
    ['Itchy', 'Painful', 'Occasionally bleeds', 'Burning sensation', 'Quickly developed', 'Oozing', 'Scaliness', 'Raised','Change in Sensation', 'None of the Above'])

for i in range(len(options)):
    #Iterates through the different options of the survey.
    #If an option is selected, ti will add the appropriate weight to the count of conditions.
    #Necessary because some symptoms are more severe than others.
    if options[i] == "Itchy":
        counter = counter+1
    if options[i] == "Painful":
        counter = counter+2
    if options[i] == "Occasionally bleeds":
        counter = counter+3
    if options[i] == "Burning sensation":
        counter = counter+2
    if options[i] == 'Quickly developed':
        counter = counter+2
    if options[i] == 'Raised':
        counter = counter+2
    if options[i] == 'Change in Sensation':
        counter = counter+2
    if options[i] == 'Oozing':
        counter = counter+2
    if options[i] == 'Scaliness':
        counter = counter+2
    if options[i] == 'None of the Above':
        counter = 0

percent = int((counter/18)*100) #Converts the weighted count to a precentage.

#Space formatting for text of the webapp
st.text('')
st.text('')

#Code for processing the image. 
if len(user_image_list) == 0:
    #If no image is provided, prompts the user to imput an image.
    st.text("Please upload an image file!")
else:
    #Otherwise, if an image is provided
    if st.button("Acknowledge Disclaimer"):
        #If the user acknowledges the disclaimer by clicking the button prompt.
        image_predictions = [] #creates a variable for storing multiple image predictions
        for user_image in user_image_list: #Iterates through all the images in the list of user images proved by the user.
            img_data = dict() #creates a dictionary for storing all images and their predicitons.

            image = Image.open(user_image) #opens the image-like element uploades as an image
            prediction = run_model(image, model) #runs the image through the model stores as in variable prediction
            img_data['image'] = image #stores each image to the dictionary with the key image.
            img_data['prediction'] = prediction #Stores each prediction to the dictionary with the key prediction.

            if np.argmax(prediction) == 0: #Takes the max argument of the prediction.
                img_data['result'] = 'Benign' #if the max was zero, then this corresponds to benign. Adds 'benign' to the dictionary with the key 'result'
            else:
                img_data['result'] = 'Malignant' #otherwise the max was one, thus the condition was malignant. Adds 'malignant' to the dictionary with the key 'result'

            image_predictions.append(img_data) #appends the dictionary of information for each image to the image_redicitons list.

        #Space formatting for text of the webapp
        st.text('')
        st.text('')

        #Creates a series of tabs for storing and moving through the multiple images provided by the user.
        tab_names = [f"Image {num}" for num in range(1, len(image_predictions)+1)] #Creates tabs with names based on the order the image was uploaded.
        tabs = st.tabs(tab_names) #Implements the tabs using streamlit's tabs method.

        for tab, image_results in zip(tabs, image_predictions):
            #Iterates through each tab adding the functionality needed for the tab.
            with tab:
                image = image_results['image'] #Gets the image stored within each tab's dictionary.
                image.thumbnail((650, 650), Image.ANTIALIAS) #Sets the image's size to be consistent for display within the tab's window.
                st.image(image) #Displays the image.

                malig_percent = round(image_results['prediction'][0][1], 2)*100 #
                benig_percent = round(image_results['prediction'][0][0], 2)*100
                malig_percent = int(round(malig_percent, 0))
                benig_percent = int(round(benig_percent, 0))
                
                col1, col2 = st.columns(2)
                col1.metric(label='**Malignant**', value=f"{malig_percent}%", delta=None)
                col2.metric(label='**Benign**', value=f"{benig_percent}%", delta=None)

                result = image_results['result']
                if result == 'Malignant':
                    st.error("Result: **" + result + "**")
                else:
                    st.success(f"Result: {result}")

        #Space formatting for text of the webapp
        st.text('')
        st.text('')
                
        averaged_prediction = average_predictions([image_results['prediction'] for image_results in image_predictions])

        #Assigns a condition to the results.
        condition = Conditions() #Calls the conditions class.
        condition.generateResults(np.argmax(averaged_prediction)) #passes the results of teh average of predictions to the conditions results generator to get information relevant to the condition.
        if condition.conditionName == "Benign":
            #If the condition is benign presents balloons to the display using streamlit's built in balloons method.
            st.balloons()
        
        #Changes the default  display
        st.markdown(subheader + 'Final Result:' + "</p>", unsafe_allow_html=True)        
        st.markdown(basic + f"Our image classifier labeled it as '{condition.conditionName}'" +"</p>", unsafe_allow_html=True)


        #Calculates the results of the user survey
        outOf = int((len(options)/9)*100)

        if percent >= 30 or options.count('Occasionally bleeds') == 1:
            st.markdown(basic + f"You have {outOf}% of the symptoms in the survey:" +"</p>", unsafe_allow_html=True) 
            st.markdown(basic + "Because of this, if you are still worried about your condition even after the results, it is recommended to see a doctor!" +"</p>", unsafe_allow_html=True) 
            
        #Presents the prediction as a nice little table of % likelihoods. 
        prediction_dict = {'Benign': [averaged_prediction[0][0]], 'Malignant': [averaged_prediction[0][1]]} #Makes a dictionary with keys of conditions and results from the model's output
        st.table(pd.DataFrame.from_dict(prediction_dict)) #Prints a table of the results on the website.



        #Plots the data from the averages of predictions as a pie chart. Formating specific to matplotlib
        benign_percent = averaged_prediction[0][0] #The percentage benign
        malignant_percent = averaged_prediction[0][1] #The percentage of malignant
        labels = ['Benign', 'Malignant'] #The labels for the pie chart
        sizes = [benign_percent, malignant_percent] #The sizes needed for the pie chart. The percentages of the two categories.

        #Creating the pie chart with matplotlib methods.
        fig1, ax1 = plt.subplots()
        explode = (0, 0.1)
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)

        ax1.axis('equal')

        st.pyplot(fig1)

        #Space formatting for text of the webapp
        st.text('')
        st.text('')

        #Presents results from the user survey based upon the weighted percent and the occurance fo specific symptoms.
        st.markdown(subheader + 'Should you seek medical help?' + "</p>", unsafe_allow_html=True)
        if condition.conditionName == 'Malignant':
            st.markdown(basic + "Because of the image results being Malignant, it is highly recommended to see a doctor!" + "</p>", unsafe_allow_html=True)
        elif percent >= 30 and condition.conditionName == 'Benign':
            st.markdown(basic + "Because of the severity of the symptoms you chose in the survery, if you are still worried about your condition even after the Benign results, it is highly recommended to see a doctor!" + "</p>", unsafe_allow_html=True)
        elif condition.conditionName == 'Benign' and options.count('None of the Above') == 1:
            st.markdown(basic + "You have no symptoms and your image results are Benign, but see a doctor if you are still concerned." + "</p>", unsafe_allow_html=True)
        else:
            st.markdown(basic + "If you are still concerned after results, see a doctor." + "</p>", unsafe_allow_html=True)


        #Presents the info for the total condition result. Presents the data from the conditon class.
        st.markdown(subheader + 'More Information:' + "</p>", unsafe_allow_html=True)
        st.markdown(basicbold + f'{condition.conditionName}' + "</p>", unsafe_allow_html=True) #presents the condition's name
        st.markdown(basic + f'{condition.description}' +"</p>", unsafe_allow_html=True) #presents the condition's description
        st.markdown(basicbold + 'Related Links:' + "</p>", unsafe_allow_html=True) #presents the condition's links to the user.
        for name,link in condition.links:
            st.write(f"[{name}]({link})")

        #Presents one final warning to the user that the webapp should not be used to provide a valid medical diagnosis.
        st.markdown(subheader + 'Remember:' + "</p>", unsafe_allow_html=True)
        st.markdown(basic + "This is an image classifier created by four students." +"</p>", unsafe_allow_html=True)
        st.markdown(basic + "It was created for a class project." +"</p>", unsafe_allow_html=True)
        st.markdown(basic + "It should not be taken as valid medical advice" +"</p>", unsafe_allow_html=True)
        st.markdown(basic + "If you are concerned about your condition see a doctor!" +"</p>", unsafe_allow_html=True) 
    else:
        #Provides the user with a disclaimer that will remain on screan until they click the 'Acknowledge Disclaimer' button.
        st.markdown(subheader + 'Acknowledge Disclaimer' + "</p>", unsafe_allow_html=True)
        st.markdown(basic + 'Before your results are processed, please acknowledge that you understand that this program does not provide valid medical advice.' + "</p>", unsafe_allow_html=True)
        st.markdown(basic + 'It is a program writen by four computer science students who have no medical experience. The project is more of a proof of concept.' + "</p>", unsafe_allow_html=True)
        st.markdown(basic + 'No classifications provided by this program should be treated as medical advice!' + "</p>", unsafe_allow_html=True)
        st.markdown(basic + 'If you are concerned about your health, visit a doctor.' + "</p>", unsafe_allow_html=True)
